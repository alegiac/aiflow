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
    ai=root/'.ai'
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
    for epic,title,status in epics:
        marker='<!-- aiflow:epic:'+epic+' -->'
        if _append_once(ai/'project.md',marker,marker+'\n- '+epic+': '+title+' ['+status+']'):
            updated.append(str(ai/'project.md'))
        tasks=db.execute('SELECT id,title,status FROM tasks WHERE epic_id=? ORDER BY id',(epic,)).fetchall()
        for task,tt,ts in tasks:
            marker='<!-- aiflow:task:'+epic+'/'+task+' -->'
            if _append_once(ai/'epics'/epic/'epic.md',marker,marker+'\n- '+task+': '+tt+' ['+ts+']'):
                updated.append(str(ai/'epics'/epic/'epic.md'))
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
        block=begin+'\\n'+'\\n'.join(inventory)+'\\n'+end
        if begin in original and end in original:
            prefix=original.split(begin,1)[0]
            suffix=original.split(end,1)[1]
            refreshed=prefix+block+suffix
        else:
            refreshed=original.rstrip()+'\\n\\n'+block+'\\n'
        if refreshed!=original:
            project.write_text(refreshed,encoding='utf-8')
            updated.append(str(project))
    # Append a timestamped state snapshot without replacing user-authored notes.
    current=ai/'state'/'current.md'
    snapshot=['## AIFlow snapshot '+_stamp(),'','### Epics']
    snapshot += ['- '+e+': '+t+' ['+s+']' for e,t,s in epics]
    snapshot += ['','### Pending decisions']
    snapshot += ['- DEC-'+str(i)+' ('+ref+'): '+stmt for i,ref,stmt in db.execute("SELECT id,ref,statement FROM decisions WHERE status='proposed' ORDER BY id")]
    if current.exists():
        with current.open('a',encoding='utf-8') as f:f.write('\n'+'\n'.join(snapshot)+'\n')
        updated.append(str(current))
    return updated


def propose(root,db,args):
    """Create draft Epic/Task markdown only on explicit command."""
    import argparse
    import sys
    from importlib.util import spec_from_file_location, module_from_spec
    cli=Path(__file__).resolve().parents[1]/'bin'/'aiflow'
    spec=spec_from_file_location('aiflow_cli',str(cli))
    if spec is None:
        from importlib.machinery import SourceFileLoader
        mod=SourceFileLoader('aiflow_cli',str(cli)).load_module()
    else:
        mod=module_from_spec(spec);spec.loader.exec_module(mod)
    if args.kind=='epic':
        mod.create_epic(root,db,argparse.Namespace(title=args.title,id=None))
    else:
        mod.create_task(root,db,argparse.Namespace(epic=args.epic,title=args.title,id=None))
    sync(root,db)

def record(root,db,args):
    """Explicit, evidence-backed canonical project or architecture specification."""
    import hashlib
    if not args.text.strip() or not args.evidence.strip() or not args.by.strip():
        raise ValueError('Non-empty text, --evidence and --by required')
    dest=root/'.ai'/('architecture.md' if args.scope=='architecture' else 'project.md')
    digest=hashlib.sha256((args.scope+'\\0'+args.text.strip()+'\\0'+args.evidence.strip()).encode()).hexdigest()[:16]
    marker='<!-- aiflow:spec:'+digest+' -->'
    section=marker+'\\n### Verified update ('+_stamp()+')\\n\\n'+args.text.strip()+'\\n\\nEvidence: '+args.evidence.strip()+'; approved by: '+args.by.strip()+'\\n'
    changed=_append_once(dest,marker,section)
    db.execute('INSERT INTO events(created_at,kind,ref,details) VALUES(?,?,?,?)',(_stamp(),'spec.record',args.scope,digest))
    db.commit()
    print('Recorded' if changed else 'Already present',dest)
