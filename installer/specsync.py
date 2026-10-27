"""Evidence-based, append-only project specification synchronization.

Only explicitly approved decisions enter canonical specs. Unapproved proposals
stay in dedicated review documents. Never overwrite human-authored sections.
"""
import datetime as dt
import json
from pathlib import Path


def _stamp():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')


def _append_once(path, marker, text):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and marker in path.read_text(encoding='utf-8'):
        return False
    with path.open('a',encoding='utf-8') as f:
        f.write('\n'+text+'\n')
    return True


def sync(root, db):
    from installer import workflows
    workflows.ensure_schema(db)
    ai=root/'.aiflow'
    updated=[]
    decisions=db.execute("SELECT id,ref,statement,rationale,approved_at,approved_by,evidence FROM decisions WHERE status='approved' ORDER BY id").fetchall()
    for number,ref,statement,rationale,approved_at,actor,evidence in decisions:
        marker='<!-- aiflow:decision:'+str(number)+' -->'
        section=(marker+'\n### Approved decision DEC-'+str(number)+' ('+ref+')\n\n'+statement+
                 '\n\nRationale: '+(rationale or 'Not specified')+
                 '\n\nApproved by: '+(actor or 'unknown')+'; evidence: '+(evidence or 'not recorded')+'; at: '+(approved_at or 'unknown')+'\n')
        if ref=='GLOBAL' or ref.startswith('PLATFORM:'):
            continue  # shared decisions have a separate governance store
        if '/' in ref:
            epic,task=ref.split('/',1)
            target=ai/'epics'/epic/'tasks'/task/'task.md'
        else:
            target=ai/'epics'/ref/'epic.md'
        if target.exists() and _append_once(target,marker,section):updated.append(str(target))
        # Cross-project architecture decisions require explicit architecture scope.
    epics=db.execute('SELECT id,title,status FROM epics ORDER BY id').fetchall()
    project=ai/'project.md'
    begin='<!-- aiflow:inventory:start -->'
    end='<!-- aiflow:inventory:end -->'
    inventory=['## AIFlow tracked scope','']
    for eid,title,status in epics:
        inventory.append('- '+eid+': '+title+' ['+status+']')
        for tid,tt,ts in db.execute('SELECT id,title,status FROM tasks WHERE epic_id=? ORDER BY id',(eid,)):
            inventory.append('  - '+tid+': '+tt+' ['+ts+']')
    if project.exists():
        original=project.read_text(encoding='utf-8')
        block=begin+'\n'+'\n'.join(inventory)+'\n'+end
        if begin in original and end in original:
            prefix=original.split(begin,1)[0]
            suffix=original.split(end,1)[1]
            refreshed=prefix+block+suffix
        else:
            refreshed=original.rstrip()+'\n\n'+block+'\n'
        if refreshed!=original:
            project.write_text(refreshed,encoding='utf-8')
            updated.append(str(project))
    # The current-state snapshot is updated only when the managed inventory changes.
    # Do not append a new timestamped block for every CLI command.
    return updated


def record(root,db,args):
    """Explicit, evidence-backed canonical project or architecture specification."""
    import hashlib
    if not args.text.strip() or not args.evidence.strip() or not args.by.strip():
        raise ValueError('Non-empty text, --evidence and --by required')
    dest=root/'.aiflow'/('architecture.md' if args.scope=='architecture' else 'project.md')
    digest=hashlib.sha256((args.scope+'\\0'+args.text.strip()+'\\0'+args.evidence.strip()).encode()).hexdigest()[:16]
    marker='<!-- aiflow:spec:'+digest+' -->'
    section=marker+'\n### Verified update ('+_stamp()+')\n\n'+args.text.strip()+'\n\nEvidence: '+args.evidence.strip()+'; approved by: '+args.by.strip()+'\n'
    changed=_append_once(dest,marker,section)
    db.execute('INSERT INTO events(created_at,kind,ref,details) VALUES(?,?,?,?)',(_stamp(),'spec.record',args.scope,digest))
    db.commit()
    print('Recorded' if changed else 'Already present',dest)
