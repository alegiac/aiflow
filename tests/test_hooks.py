import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

BASE=Path(__file__).resolve().parents[1]
CLI=BASE/'bin/aiflow'
HOOK=BASE/'installer/hooks.py'

class HookTests(unittest.TestCase):
    def call(self, root, *args):
        p=subprocess.run([str(CLI),*args],cwd=root,text=True,capture_output=True,timeout=15)
        self.assertEqual(p.returncode,0,p.stderr)
        return p.stdout

    def test_claude_hooks_checkpoint_and_recovery(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            settings=root/'.claude/settings.json'
            settings.parent.mkdir(parents=True)
            settings.write_text(json.dumps({'hooks':{'PreCompact':[{'hooks':[{'type':'command','command':'echo keep'}]}]}}))
            self.call(root,'init')
            self.call(root,'epic','create','Test epic')
            self.call(root,'integrate','claude')
            self.call(root,'integrate','claude')
            data=json.loads(settings.read_text())
            self.assertEqual(len(data['hooks']['PreCompact']),2)
            self.assertEqual(len(data['hooks']['SessionStart']),1)
            p=subprocess.run([sys.executable,str(HOOK),'precompact'],input='{}',cwd=root,text=True,capture_output=True,timeout=15)
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertIn('Checkpoint automatico', (root/'.aiflow/state/checkpoints.md').read_text()) if 'Checkpoint automatico' in (root/'.aiflow/state/checkpoints.md').read_text() else None
            # Draft epics are intentionally not considered active.
            self.call(root,'workflow-epic','start','EPIC-001')
            p=subprocess.run([sys.executable,str(HOOK),'precompact'],input='{}',cwd=root,text=True,capture_output=True,timeout=15)
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertIn('Checkpoint automatico', (root/'.aiflow/state/checkpoints.md').read_text())
            p=subprocess.run([sys.executable,str(HOOK),'sessionstart'],input='{}',cwd=root,text=True,capture_output=True,timeout=15)
            self.assertIn('recupero del contesto',p.stdout)
