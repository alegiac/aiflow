"""AIFlow durable workflow operations. Standard library only."""
import datetime as dt
import json
import re
import sqlite3
from pathlib import Path


def timestamp():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')


def append(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as f:
        f.write(content)


def log(db, kind, ref, details):
    db.execute('INSERT INTO events(created_at,kind,ref,details) VALUES(?,?,?,?)', (timestamp(), kind, ref, details))


def validate_ref(root, db, ref):
    if not ref or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{1,63}(?:/[A-Za-z][A-Za-z0-9_-]{1,63})?', ref):
        raise ValueError('Riferimento non valido: usa EPIC-ID oppure EPIC-ID/TASK-ID')
    parts = ref.split('/')
    if not db.execute('SELECT 1 FROM epics WHERE id=?', (parts[0],)).fetchone():
        raise ValueError('Epic inesistente')
    path = root/'.aiflow/epics'/parts[0]
    if len(parts) == 2:
        if not db.execute('SELECT 1 FROM tasks WHERE epic_id=? AND id=?', tuple(parts)).fetchone():
            raise ValueError('Task inesistente')
        path = path/'tasks'/parts[1]
    return path


def ensure_schema(db):
    db.executescript('''
    CREATE TABLE IF NOT EXISTS decisions (
      id INTEGER PRIMARY KEY AUTOINCREMENT, ref TEXT NOT NULL, statement TEXT NOT NULL,
      rationale TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'proposed',
      proposed_at TEXT NOT NULL, approved_at TEXT, approved_by TEXT, evidence TEXT);
    CREATE TABLE IF NOT EXISTS checkpoints (
      id INTEGER PRIMARY KEY AUTOINCREMENT, ref TEXT NOT NULL, summary TEXT NOT NULL,
      next_step TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS approvals (
      id INTEGER PRIMARY KEY AUTOINCREMENT, ref TEXT NOT NULL, kind TEXT NOT NULL,
      actor TEXT NOT NULL, evidence TEXT NOT NULL, created_at TEXT NOT NULL);
    ''')


def central_db():
    import os
    base = Path(os.environ.get('AIFLOW_HOME', str(Path.home()/'.config'/'aiflow'))).expanduser()
    base.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(base/'governance.sqlite3')
    con.execute("PRAGMA busy_timeout=5000")
    ensure_schema(con)
    con.execute('CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT, kind TEXT, ref TEXT, details TEXT)')
    return con


def decision_scope(root, db, ref):
    if ref == 'GLOBAL':
        return central_db(), Path(__import__('os').environ.get('AIFLOW_HOME', str(Path.home()/'.config'/'aiflow')))/'global'
    if ref.startswith('PLATFORM:'):
        name = ref.split(':', 1)[1]
        if not re.fullmatch(r'[a-z][a-z0-9-]{1,63}', name):
            raise ValueError('Nome piattaforma non valido')
        return central_db(), Path(__import__('os').environ.get('AIFLOW_HOME', str(Path.home()/'.config'/'aiflow')))/'platforms'/name
    return db, validate_ref(root, db, ref)


def decision(root, db, args):
    ensure_schema(db)
    if args.action == 'propose':
        store, path = decision_scope(root, db, args.ref)
        with store:
            cur = store.execute('INSERT INTO decisions(ref,statement,rationale,proposed_at) VALUES(?,?,?,?)',
                             (args.ref, args.text, args.rationale or '', timestamp()))
            number = cur.lastrowid
            log(store, 'decision.proposed', args.ref, str(number))
        append(path/'decisions.md', f'\n## DEC-{number:04d} — PROPOSTA\n\n{args.text}\n\nMotivazione: {args.rationale or "Da definire"}\n')
        print(f'DEC-{number:04d} proposta; non approvata')
    elif args.action == 'approve':
        if not args.by.strip() or not args.evidence.strip():
            raise ValueError('Richiesta approvazione esplicita: --by e --evidence')
        store = central_db() if getattr(args, 'ref', None) in ('GLOBAL',) or (getattr(args, 'ref', '') or '').startswith('PLATFORM:') else db
        row = store.execute('SELECT ref,statement,status FROM decisions WHERE id=?', (args.id,)).fetchone()
        if not row or row[2] != 'proposed':
            raise ValueError('Decisione inesistente o non più proposta')
        _, path = decision_scope(root, db, row[0])
        with store:
            store.execute('UPDATE decisions SET status=?,approved_at=?,approved_by=?,evidence=? WHERE id=?',
                       ('approved', timestamp(), args.by, args.evidence, args.id))
            log(store, 'decision.approved', row[0], f'DEC-{args.id:04d} by {args.by}: {args.evidence}')
        append(path/'decisions.md', f'\n### DEC-{args.id:04d} — APPROVATA ({timestamp()})\n\nDa: {args.by}\nConferma: {args.evidence}\n')
        print(f'DEC-{args.id:04d} approvata')
    else:
        for label, store in [('PROJECT', db), ('SHARED', central_db())]:
            for r in store.execute('SELECT id,ref,status,statement FROM decisions ORDER BY id'):
                print(f'{label} DEC-{r[0]:04d} | {r[1]} | {r[2]} | {r[3]}')
            if store is not db: store.close()


def approval(root, db, args):
    ensure_schema(db)
    path = validate_ref(root, db, args.ref)
    if not args.by.strip() or not args.evidence.strip():
        raise ValueError('Approvazione esplicita richiesta: --by e --evidence')
    with db:
        db.execute('INSERT INTO approvals(ref,kind,actor,evidence,created_at) VALUES(?,?,?,?,?)',
                   (args.ref,args.kind,args.by,args.evidence,timestamp()))
        log(db,'approval.'+args.kind,args.ref,args.evidence)
    append(path/'approvals.md',f'\n## {timestamp()} — {args.kind}\n\nApprovato da: {args.by}\nConferma: {args.evidence}\n')
    print('Approvazione registrata:', args.ref, args.kind)


def checkpoint(root, db, args):
    ensure_schema(db)
    path = validate_ref(root, db, args.ref)
    with db:
        cur = db.execute('INSERT INTO checkpoints(ref,summary,next_step,created_at) VALUES(?,?,?,?)',
                         (args.ref,args.summary,args.next or '',timestamp()))
        log(db,'checkpoint',args.ref,str(cur.lastrowid))
    entry=f'\n## CP-{cur.lastrowid:04d} — {timestamp()} — {args.ref}\n\n{args.summary}\n\n**Prossimo passo:** {args.next or "Da concordare"}\n'
    append(root/'.aiflow/state/checkpoints.md',entry)
    append(path/'checkpoints.md',entry)
    print(f'Checkpoint CP-{cur.lastrowid:04d} registrato')


def lifecycle(root, db, args):
    ensure_schema(db)
    if args.kind == 'task':
        ref=f'{args.epic}/{args.id}'
    else:
        ref=args.id
    path=validate_ref(root,db,ref)
    if args.kind=='epic' and args.action=='approve':
        missing=[k for k in ('scope','requirements','plan') if not db.execute('SELECT 1 FROM approvals WHERE ref=? AND kind=?',(ref,k)).fetchone()]
        if missing: raise ValueError('Epic non approvabile; mancano approvazioni: '+', '.join(missing))
    if args.kind=='task' and args.action=='start':
        epic=db.execute('SELECT status FROM epics WHERE id=?',(args.epic,)).fetchone()
        if epic[0] not in ('approved','active'): raise ValueError('Approva prima l’Epic e il piano dei Task')
    if args.kind=='task' and args.action=='finish':
        current=db.execute('SELECT status FROM tasks WHERE epic_id=? AND id=?',(args.epic,args.id)).fetchone()[0]
        if current!='review': raise ValueError('Il Task deve essere in review prima della chiusura')
        if not db.execute('SELECT 1 FROM approvals WHERE ref=? AND kind=?',(ref,'acceptance')).fetchone():
            raise ValueError('Manca l’approvazione esplicita dei criteri di accettazione')
    if args.kind=='epic' and args.action=='finish':
        current=db.execute('SELECT status FROM epics WHERE id=?',(args.id,)).fetchone()[0]
        if current not in ('approved','active'): raise ValueError('Epic non approvata/attiva')
    if args.action in ('approve','finish'):
        if not args.by or not args.evidence:
            raise ValueError('Per approvare/chiudere serve --by e --evidence (conferma umana reale)')
        with db:
            db.execute('INSERT INTO approvals(ref,kind,actor,evidence,created_at) VALUES(?,?,?,?,?)',
                       (ref,args.action,args.by,args.evidence,timestamp()))
    if args.kind=='task':
        status={'start':'active','review':'review','finish':'completed'}[args.action]
        with db:
            db.execute('UPDATE tasks SET status=?,updated_at=? WHERE epic_id=? AND id=?',
                       (status,timestamp(),args.epic,args.id))
            log(db,'task.'+args.action,ref,args.evidence or '')
        file=path/'task.md'
    else:
        status={'start':'active','approve':'approved','finish':'completed'}[args.action]
        if args.action=='finish':
            open_tasks=db.execute("SELECT COUNT(*) FROM tasks WHERE epic_id=? AND status NOT IN ('completed','cancelled')",(args.id,)).fetchone()[0]
            if open_tasks: raise ValueError(f'Epic contiene {open_tasks} task non conclusi')
        with db:
            db.execute('UPDATE epics SET status=?,updated_at=? WHERE id=?',(status,timestamp(),args.id))
            log(db,'epic.'+args.action,ref,args.evidence or '')
        file=path/'epic.md'
    text=file.read_text(encoding='utf-8')
    text=re.sub(r'(?m)^- Stato: .*$',f'- Stato: {status}',text,count=1)
    file.write_text(text,encoding='utf-8')
    append(path/('report.md' if args.kind=='task' else 'epic.md'),
           f'\n## Workflow {args.action} — {timestamp()}\n\n{args.evidence or "Avvio operativo"}\n')
    print(ref,'→',status)


def recovery(root, db, args):
    ensure_schema(db)
    print('# AIFlow — recupero del contesto')
    print('\nLeggere `.aiflow/AGENTS.md`, `.aiflow/project.md`, `.aiflow/architecture.md` e i documenti della Epic/Task attiva.')
    for row in db.execute("SELECT id,title,status FROM epics WHERE status NOT IN ('completed','cancelled') ORDER BY updated_at DESC LIMIT 10"):
        print(f'\nEpic {row[0]} [{row[2]}] {row[1]}')
        for task in db.execute('SELECT id,title,status FROM tasks WHERE epic_id=? ORDER BY updated_at DESC',(row[0],)):
            print(f'  {row[0]}/{task[0]} [{task[2]}] {task[1]}')
    print('\n## Ultimi checkpoint')
    for cp in db.execute('SELECT ref,summary,next_step FROM checkpoints ORDER BY id DESC LIMIT 5'):
        print(f'- {cp[0]}: {cp[1]} | Prossimo: {cp[2]}')
    print('\n## Decisioni ancora da approvare')
    for dec in db.execute("SELECT id,ref,statement FROM decisions WHERE status='proposed' ORDER BY id DESC LIMIT 10"):
        print(f'- DEC-{dec[0]:04d} {dec[1]}: {dec[2]}')
    print('\n## Sessione e tracking')
    s=db.execute('SELECT id,started_at FROM sessions WHERE ended_at IS NULL').fetchone()
    t=db.execute('SELECT id,epic_id,task_id FROM activities WHERE ended_at IS NULL').fetchone()
    print('Sessione:',s or 'nessuna','| Tracking:',t or 'nessuno')
    print('\nPrima di continuare, verificare eventuali modifiche non committate e riallineare i documenti.')


def report(root, db, args):
    """Deterministic report based only on recorded events, durations and approvals."""
    ensure_schema(db)
    ref=args.ref
    if ref!='project': validate_ref(root,db,ref)
    def belongs(r):
        return ref=='project' or r==ref or (ref.count('/')==0 and r.startswith(ref+'/'))
    lines=['# AIFlow — Resoconto '+ref,'',f'Generato: {timestamp()}','']
    if ref=='project':
        lines+=['## Epic']+[f'- {i}: {t} [{s}]' for i,t,s in db.execute('SELECT id,title,status FROM epics ORDER BY id')]+['']
    elif '/' not in ref:
        lines+=['## Task']+[f'- {i}: {t} [{s}]' for i,t,s in db.execute('SELECT id,title,status FROM tasks WHERE epic_id=? ORDER BY id',(ref,))]+['']
    lines+=['## Attività e tempi']
    total=0
    for epic,task,start,end,note in db.execute('SELECT epic_id,task_id,started_at,ended_at,note FROM activities ORDER BY id'):
        r=(epic or '')+('/'+task if task else '')
        if not belongs(r): continue
        minutes=round((dt.datetime.fromisoformat(end)-dt.datetime.fromisoformat(start)).total_seconds()/60,2) if end else None
        if minutes is not None: total+=minutes
        lines.append(f'- {r or "generale"}: {minutes if minutes is not None else "in corso"} min — {note or "nessuna nota"}')
    lines += [f'**Totale attività concluse:** {round(total,2)} minuti','', '## Decisioni']
    for i,r,st,statement in db.execute('SELECT id,ref,status,statement FROM decisions ORDER BY id'):
        if belongs(r): lines.append(f'- DEC-{i:04d} [{st}] {r}: {statement}')
    lines+=['','## Approvazioni']
    for r,k,actor,evidence in db.execute('SELECT ref,kind,actor,evidence FROM approvals ORDER BY id'):
        if belongs(r): lines.append(f'- {r} / {k} — {actor}: {evidence}')
    lines+=['','## Checkpoint']
    for r,summary,next_step in db.execute('SELECT ref,summary,next_step FROM checkpoints ORDER BY id'):
        if belongs(r): lines.append(f'- {r}: {summary} | Prossimo: {next_step}')
    output='\n'.join(lines)+'\n'
    if args.output:
        target=Path(args.output).resolve()
    else:
        target=(root/'.aiflow/state/project-report.md' if ref=='project' else validate_ref(root,db,ref)/('report.md' if '/' in ref else 'summary.md'))
    target.parent.mkdir(parents=True,exist_ok=True)
    # Generated reports are separate from manually curated task reports.
    if not args.output and '/' in ref: target=target.with_name('activity-summary.md')
    target.write_text(output,encoding='utf-8')
    print('Resoconto:',target)
