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
    def test_unrelated_ai_directory_is_preserved_during_init(self):
        legacy=self.root/'.ai'
        legacy.mkdir()
        (legacy/'notes.txt').write_text('legacy project content')
        self.cli('init')
        self.cli('status')
        self.cli('day','start')
        self.cli('day','end','--no-digest')
        self.assertEqual((legacy/'notes.txt').read_text(),'legacy project content')
        self.assertTrue((self.root/'.aiflow/state/aiflow.sqlite3').exists())

    def test_unrelated_ai_directory_is_preserved_during_adopt(self):
        legacy=self.root/'.ai'
        legacy.mkdir()
        (legacy/'notes.txt').write_text('external data')
        (self.root/'composer.json').write_text('{"require":{"laravel/framework":"^13.0"}}')
        self.cli('adopt')
        self.cli('adopt','--apply')
        self.assertEqual((legacy/'notes.txt').read_text(),'external data')
        self.assertTrue((self.root/'.aiflow/adoption-review.json').exists())

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
        self.assertFalse((self.root/'.aiflow').exists())
        self.cli('adopt','--apply')
        self.assertTrue((self.root/'.aiflow/adoption-review.json').exists())
        self.assertTrue((self.root/'.aiflow/adoption-review.md').exists())
        self.assertNotEqual(self.cli('adopt','--apply',ok=False).returncode,0)
    def test_adoption_conversation_is_review_only(self):
        (self.root/'package.json').write_text('{"dependencies":{"react":"^19"}}')
        conversation=self.root/'conversation.md'
        conversation.write_text('We decided to implement the user dashboard tomorrow.\n')
        self.cli('adopt','--conversation',str(conversation),'--apply')
        report=json.loads((self.root/'.aiflow/adoption-review.json').read_text())
        self.assertGreaterEqual(report['conversation']['characters'],10)
        self.assertFalse(list((self.root/'.aiflow/epics').iterdir()))
    def test_tracker_is_not_exposed(self):
        self.cli('init')
        self.assertNotIn('tracker',self.cli('--help').stdout)

    def test_specs_are_markdown_backed_and_sync_is_idempotent(self):
        self.cli('init')
        self.cli('epic','create','Billing')
        self.cli('task','create','EPIC-001','Invoice PDF')
        epic=self.root/'.aiflow/epics/EPIC-001/epic.md'
        task=self.root/'.aiflow/epics/EPIC-001/tasks/TASK-001/task.md'
        self.assertTrue(epic.exists())
        self.assertTrue(task.exists())
        self.cli('specs','sync')
        self.cli('specs','sync')
        self.assertEqual((self.root/'.aiflow/project.md').read_text().count('<!-- aiflow:inventory:start -->'),1)
        self.assertIn('TASK-001: Invoice PDF', (self.root/'.aiflow/project.md').read_text())
        self.assertIn('Billing',epic.read_text())
        self.cli('day','start')
        self.cli('day','end','--summary','Done','--next','Next task')
        self.assertIn('Done',(self.root/'.aiflow/state/checkpoints.md').read_text())

    def test_evidence_backed_architecture_update(self):
        self.cli('init')
        self.cli('specs','record','architecture','PostgreSQL persistence','--by','user','--evidence','Reviewed ADR')
        self.cli('specs','record','architecture','PostgreSQL persistence','--by','user','--evidence','Reviewed ADR')
        doc=(self.root/'.aiflow/architecture.md').read_text()
        self.assertEqual(doc.count('PostgreSQL persistence'),1)
        self.assertIn('Reviewed ADR',doc)

    def test_create_auto_sync_and_no_duplicate_propose(self):
        self.cli('init')
        self.assertNotIn('propose',self.cli('specs','--help').stdout)
        self.cli('epic','create','Payments')
        project=self.root/'.aiflow/project.md'
        self.assertIn('EPIC-001: Payments [draft]',project.read_text())
        self.cli('task','create','EPIC-001','Card capture')
        self.assertIn('TASK-001: Card capture [draft]',project.read_text())
        self.cli('task','status','EPIC-001','TASK-001','blocked')
        self.assertIn('TASK-001: Card capture [blocked]',project.read_text())
        before=project.read_text()
        self.cli('specs','sync')
        self.assertEqual(before,project.read_text())
        self.assertEqual(project.read_text().count('<!-- aiflow:inventory:start -->'),1)

    def test_adopt_force_preserves_initialized_project(self):
        (self.root/'composer.json').write_text('{"require":{"laravel/framework":"^13.0"}}')
        self.cli('init')
        cfg=self.root/'.aiflow/config.json'
        project=self.root/'.aiflow/project.md'
        original_cfg=cfg.read_bytes()
        self.cli('epic','create','Existing epic')
        original_project=project.read_bytes()
        epic=self.root/'.aiflow/epics/EPIC-001/epic.md'
        original_epic=epic.read_bytes()
        self.assertNotEqual(self.cli('adopt','--apply',ok=False).returncode,0)
        self.assertNotEqual(self.cli('adopt','--force',ok=False).returncode,0)
        self.cli('adopt','--apply','--force')
        self.assertEqual(cfg.read_bytes(),original_cfg)
        self.assertEqual(project.read_bytes(),original_project)
        self.assertEqual(epic.read_bytes(),original_epic)
        self.assertTrue((self.root/'.aiflow/adoption-review.md').exists())
        self.assertTrue((self.root/'.aiflow/adoption-review.json').exists())
        self.assertTrue(json.loads((self.root/'.aiflow/adoption-review.json').read_text())['existing_initialization_preserved'])
        self.assertNotEqual(self.cli('adopt','--apply','--force',ok=False).returncode,0)
