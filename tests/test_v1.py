import os
from pathlib import Path
import subprocess
import tempfile
import unittest
CLI=Path(__file__).resolve().parents[1]/'bin/aiflow'
class V1Tests(unittest.TestCase):
    def test_full_lifecycle_and_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            env={**os.environ,'AIFLOW_PROJECT':tmp}
            def run(*args,ok=True):
                p=subprocess.run([str(CLI),*args],env=env,capture_output=True,text=True,timeout=12)
                if ok: self.assertEqual(p.returncode,0,p.stderr)
                return p
            run('init')
            run('epic','create','Authentication','--id','EPIC-009')
            run('epic','create','Orders')
            self.assertIn('EPIC-010',run('epic','list').stdout)
            run('task','create','EPIC-009','Login')
            self.assertNotEqual(run('workflow-task','start','EPIC-009','TASK-001',ok=False).returncode,0)
            for kind in ('scope','requirements','plan'):
                run('approve','EPIC-009',kind,'--by','human','--evidence','Confirmed in chat')
            run('workflow-epic','approve','EPIC-009','--by','human','--evidence','Confirmed in chat')
            run('workflow-task','start','EPIC-009','TASK-001')
            run('workflow-task','review','EPIC-009','TASK-001')
            self.assertNotEqual(run('workflow-task','finish','EPIC-009','TASK-001','--by','human','--evidence','Done',ok=False).returncode,0)
            run('approve','EPIC-009/TASK-001','acceptance','--by','human','--evidence','Validated')
            run('workflow-task','finish','EPIC-009','TASK-001','--by','human','--evidence','Validated')
            run('workflow-epic','finish','EPIC-009','--by','human','--evidence','Validated')
            run('report','EPIC-009')
            self.assertTrue((Path(tmp)/'.aiflow/epics/EPIC-009/summary.md').exists())
            run('report','EPIC-009/TASK-001')
            self.assertTrue((Path(tmp)/'.aiflow/epics/EPIC-009/tasks/TASK-001/activity-summary.md').exists())
