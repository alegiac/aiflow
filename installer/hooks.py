"""Claude Code project hooks: fail-open, local, no network or privileged actions."""
import json
import sys
from pathlib import Path


def run():
    # Claude hooks provide event metadata on stdin. Never persist raw hook input:
    # it may contain private conversation material.
    try:
        payload = json.load(sys.stdin)
    except (ValueError, EOFError):
        payload = {}
    root = Path.cwd()
    if not (root / '.ai/state/aiflow.sqlite3').exists():
        return
    from importlib.machinery import SourceFileLoader
    from importlib.util import spec_from_loader, module_from_spec
    cli_path = Path(__file__).resolve().parents[1] / 'bin/aiflow'
    loader = SourceFileLoader('aiflow_cli_hook', str(cli_path))
    spec = spec_from_loader(loader.name, loader)
    module = module_from_spec(spec)
    loader.exec_module(module)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from installer import workflows
    db = module.connect(root)
    workflows.ensure_schema(db)
    action = sys.argv[1] if len(sys.argv)>1 else ''
    if action == 'precompact':
        # A truthful mechanical checkpoint, not a fabricated analysis summary.
        active = db.execute("SELECT epic_id,task_id FROM activities WHERE ended_at IS NULL ORDER BY id DESC LIMIT 1").fetchone()
        if active and active[0]:
            ref = active[0] + ('/' + active[1] if active[1] else '')
        else:
            row = db.execute("SELECT id FROM epics WHERE status IN ('active','analysis') ORDER BY updated_at DESC LIMIT 1").fetchone()
            ref = row[0] if row else None
        if ref:
            args = type('Args', (), {'ref':ref, 'summary':'Checkpoint automatico prima della compattazione. Consultare documenti, decisioni e modifiche non committate; questo evento non attesta completamento o approvazione.', 'next':'Eseguire aiflow recover e verificare git status prima di continuare.'})()
            workflows.checkpoint(root, db, args)
    elif action == 'sessionstart':
        workflows.recovery(root, db, None)
    db.close()

if __name__ == '__main__':
    try:
        run()
    except Exception as exc:
        # Hooks must not prevent the user's editor/agent from working.
        print('AIFlow hook warning: ' + str(exc), file=sys.stderr)
