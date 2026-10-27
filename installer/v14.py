"""AIFlow v1.4 daily workflow and safe existing-project adoption."""
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess


def _today():
    return dt.datetime.now().astimezone().date().isoformat()


def day(root, db, args):
    date = args.date or _today()
    try:
        dt.date.fromisoformat(date)
    except ValueError:
        raise ValueError('Invalid date: use YYYY-MM-DD')
    if args.action == 'start':
        from installer import specsync
        specsync.sync(root,db)
        existing = db.execute("SELECT id FROM sessions WHERE ended_at IS NULL ORDER BY id DESC LIMIT 1").fetchone()
        if not existing:
            now = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
            db.execute('INSERT INTO sessions(started_at,note) VALUES(?,?)', (now, 'AIFlow day ' + date))
            db.execute('INSERT INTO events(created_at,kind,ref,details) VALUES(?,?,?,?)', (now,'day.start',date,''))
            db.commit()
        session = db.execute("SELECT id,started_at FROM sessions WHERE ended_at IS NULL ORDER BY id DESC LIMIT 1").fetchone()
        tasks = [dict(epic=r[0], task=r[1], title=r[2], status=r[3]) for r in db.execute("SELECT epic_id,id,title,status FROM tasks WHERE status NOT IN ('done','completed') ORDER BY updated_at DESC LIMIT 15")]
        result = dict(date=date, session_id=session[0], resumed=bool(existing), tasks=tasks)
        if args.json: print(json.dumps(result,ensure_ascii=False,indent=2))
        else:
            print('AIFlow day start:',date,'(resumed)' if existing else '(new)')
            print('Session:',session[0])
            for t in tasks: print(' ',t['epic']+'/'+t['task'], '['+t['status']+']', t['title'])
        return
    row = db.execute("SELECT id FROM sessions WHERE ended_at IS NULL ORDER BY id DESC LIMIT 1").fetchone()
    active = db.execute("SELECT id,epic_id,task_id,started_at FROM activities WHERE ended_at IS NULL ORDER BY id DESC LIMIT 1").fetchone()
    if not row and not active:
        result = dict(date=date,already_closed=True)
        print(json.dumps(result) if args.json else 'Day already closed')
        return
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
    if active: db.execute('UPDATE activities SET ended_at=? WHERE id=?',(now,active[0]))
    if row: db.execute('UPDATE sessions SET ended_at=? WHERE id=?',(now,row[0]))
    summary = args.summary or 'Day closed; review open tasks and next steps'
    db.execute('INSERT INTO events(created_at,kind,ref,details) VALUES(?,?,?,?)',(now,'day.end',date,summary))
    from installer import workflows
    workflows.ensure_schema(db)
    next_step = args.next or 'Review open tasks at next day start'
    ref = 'project'
    db.execute('INSERT INTO checkpoints(ref,summary,next_step,created_at) VALUES(?,?,?,?)',(ref,summary,next_step,now))
    db.commit()
    from installer import specsync
    updated=specsync.sync(root,db)
    checkpoint_path=root/'.ai'/'state'/'checkpoints.md'
    with checkpoint_path.open('a',encoding='utf-8') as f:
        f.write('\\n## Day '+date+' — '+now+'\\n\\n'+summary+'\\n\\nNext: '+next_step+'\\n')
    result = dict(date=date,updated_specs=len(updated),session_id=row[0] if row else None,stopped_activity=active[0] if active else None,summary=summary)
    if args.json: print(json.dumps(result,ensure_ascii=False,indent=2))
    else: print('AIFlow day end:',date,'\n',summary)


def _git(root, *args):
    try:
        return subprocess.run(['git','-C',str(root),*args],capture_output=True,text=True,timeout=8,check=True).stdout.strip()
    except (OSError,subprocess.SubprocessError):
        return ''


def adopt(root, args):
    if not root.is_dir(): raise ValueError('Project directory not found')
    if (root/'.ai'/'config.json').exists(): raise ValueError('AIFlow already initialized: refusing to overwrite')
    skip={'.git','.ai','node_modules','vendor','.venv','venv','dist','build'}
    names=[]
    for p in sorted(root.iterdir()):
        if p.name not in skip: names.append(p.name)
    evidence=[]
    detected=[]
    markers={'composer.json':'php-laravel','package.json':'nodejs','artisan':'php-laravel','vite.config.ts':'react','vite.config.js':'react','next.config.js':'react','next.config.ts':'react','next.config.mjs':'react','tailwind.config.js':'tailwind','tailwind.config.ts':'tailwind'}
    for filename, profile in markers.items():
        if (root/filename).exists():
            evidence.append(filename)
            if profile not in detected: detected.append(profile)
    for filename in ('composer.json','package.json'):
        p=root/filename
        if p.exists() and p.stat().st_size<250000:
            try:
                d=json.loads(p.read_text(encoding='utf-8'))
                deps={**d.get('require',{}),**d.get('require-dev',{}),**d.get('dependencies',{}),**d.get('devDependencies',{})}
                for token,profile in [('laravel/framework','php-laravel'),('react','react'),('tailwindcss','tailwind'),('pg','postgresql'),('mysql2','mysql')]:
                    if token in deps and profile not in detected: detected.append(profile)
            except (ValueError,UnicodeError): pass
    history=_git(root,'log','-8','--pretty=format:%h %s')
    branch=_git(root,'branch','--show-current')
    conversation=None
    proposals=[]
    if args.conversation:
        file=Path(args.conversation).expanduser().resolve()
        if not file.is_file() or file.stat().st_size>2_000_000: raise ValueError('Conversation export missing or larger than 2 MB')
        if file.suffix.lower() not in ('.txt','.md','.json'): raise ValueError('Only txt, md, json conversation exports supported')
        raw=file.read_text(encoding='utf-8')
        import hashlib
        # Extract review candidates, not approved decisions. Keep transcript outside project.
        for line in raw.splitlines():
            stripped=line.strip()
            if len(stripped)>20 and re.search(r'(?i)\\b(todo|task|epic|decision|deciso|implementare|fixme|bug)\\b',stripped):
                proposals.append(dict(source='conversation:'+file.name,excerpt=stripped[:300],status='needs-review'))
                if len(proposals)>=100: break
        conversation=dict(path=str(file),characters=len(raw),sha256=hashlib.sha256(raw.encode()).hexdigest(),review_candidates=len(proposals))
    report=dict(project=str(root),branch=branch,top_level=names[:100],profiles=detected,evidence=evidence,recent_commits=history.splitlines(),conversation=conversation,proposals=proposals,warning='Inferred facts need human review; conversation is not automatically imported from provider private history')
    if not args.apply:
        print(json.dumps(report,ensure_ascii=False,indent=2))
        print('DRY RUN: no files changed. Use --apply to initialize and write a review report.')
        return
    # Invoke the existing CLI init to preserve schema and scaffolding behavior.
    cli=Path(__file__).resolve().parents[1]/'bin'/'aiflow'
    profiles=detected or ['php-laravel']
    available={p.parent.name for p in (Path(__file__).resolve().parents[1]/'profiles').glob('*/PROFILE.md')}
    profiles=[p for p in profiles if p in available] or ['php-laravel']
    env=os.environ.copy(); env['AIFLOW_PROJECT']=str(root)
    result=subprocess.run([os.environ.get('PYTHON',os.sys.executable),str(cli),'init','--profile',','.join(profiles)],cwd=root,env=env,check=False)
    if result.returncode: raise ValueError('Initialization failed; inspect project before retrying')
    report_path=root/'.ai'/'adoption-review.json'
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    review=root/'.ai'/'adoption-review.md'
    lines=['# Adoption review (not approved)','', '## Evidence', *('- '+e for e in evidence),'','## Recent commits',*('- '+c for c in history.splitlines()),'','## Conversation candidates (unverified)',*('- '+p['excerpt'] for p in proposals),'','Review and explicitly approve before creating epics/tasks or accepting decisions.']
    review.write_text('\\n'.join(lines)+'\\n',encoding='utf-8')
    print('Adoption report:',report_path,'\nReview findings before approving any decisions.')
