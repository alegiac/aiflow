import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CLI=Path(__file__).resolve().parents[1]/'bin'/'aiflow'

class TestV14(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
    def cli(self,*args,ok=True):
        env=os.environ.copy()
        env['AIFLOW_PROJECT']=str(self.root)
        p=subprocess.run([sys.executable,str(CLI),*args],cwd=self.root,env=env,text=True,capture_output=True)
        if ok:self.assertEqual(p.returncode,0,p.stderr)
        return p
    def test_daily_resume_and_checkpoint(self):
        self.cli('init')
        first=json.loads(self.cli('day','start','--json').stdout)
        self.assertFalse(first['resumed'])
        again=json.loads(self.cli('day','start','--json').stdout)
        self.assertTrue(again['resumed'])
        self.assertEqual(first['session_id'],again['session_id'])
        self.cli('day','end','--summary','Finished API','--next','Run tests')
        self.assertIn('already closed',self.cli('day','end').stdout.lower())
        self.assertIn('Finished API',self.cli('recover').stdout)
    def test_adoption_preview_and_apply(self):
        (self.root/'composer.json').write_text('{"require":{"laravel/framework":"^13.0"}}')
        preview=self.cli('adopt').stdout
        self.assertIn('php-laravel',preview)
        self.assertFalse((self.root/'.ai').exists())
        self.cli('adopt','--apply')
        self.assertTrue((self.root/'.ai/adoption-review.json').exists())
        self.assertTrue((self.root/'.ai/adoption-review.md').exists())
        self.assertNotEqual(self.cli('adopt','--apply',ok=False).returncode,0)
    def test_adoption_conversation_is_review_only(self):
        (self.root/'package.json').write_text('{"dependencies":{"react":"^19"}}')
        conversation=self.root/'conversation.md'
        conversation.write_text('We decided to implement the user dashboard tomorrow.\n')
        self.cli('adopt','--conversation',str(conversation),'--apply')
        report=json.loads((self.root/'.ai/adoption-review.json').read_text())
        self.assertGreaterEqual(report['conversation']['characters'],10)
        self.assertFalse(list((self.root/'.ai/epics').iterdir()))
    def test_tracker_is_not_exposed(self):
        self.cli('init')
        self.assertNotIn('tracker',self.cli('--help').stdout)

    def test_specs_are_markdown_backed_and_sync_is_idempotent(self):
        self.cli('init')
        self.cli('specs','propose','epic','Billing')
        self.cli('specs','propose','task','Invoice PDF','--epic','EPIC-001')
        epic=self.root/'.ai/epics/EPIC-001/epic.md'
        task=self.root/'.ai/epics/EPIC-001/tasks/TASK-001/task.md'
        self.assertTrue(epic.exists())
        self.assertTrue(task.exists())
        self.cli('specs','sync')
        self.cli('specs','sync')
        self.assertEqual((self.root/'.ai/project.md').read_text().count('<!-- aiflow:epic:EPIC-001 -->'),1)
        self.assertEqual(epic.read_text().count('<!-- aiflow:task:EPIC-001/TASK-001 -->'),1)
        self.cli('day','start')
        self.cli('day','end','--summary','Done','--next','Next task')
        self.assertIn('Done',(self.root/'.ai/state/checkpoints.md').read_text())

    def test_evidence_backed_architecture_update(self):
        self.cli('init')
        self.cli('specs','record','architecture','PostgreSQL persistence','--by','user','--evidence','Reviewed ADR')
        self.cli('specs','record','architecture','PostgreSQL persistence','--by','user','--evidence','Reviewed ADR')
        doc=(self.root/'.ai/architecture.md').read_text()
        self.assertEqual(doc.count('PostgreSQL persistence'),1)
        self.assertIn('Reviewed ADR',doc)
