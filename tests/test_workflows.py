import os
from pathlib import Path
import subprocess
import tempfile
import unittest

CLI=Path(__file__).resolve().parents[1]/'bin'/'aiflow'
class TestWorkflows(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.run_cli('init')
    def run_cli(self,*args,ok=True):
        env=os.environ.copy(); env['AIFLOW_PROJECT']=str(self.root)
        p=subprocess.run([str(CLI),*args],capture_output=True,text=True,env=env)
        if ok: self.assertEqual(p.returncode,0,p.stderr)
        return p
    def test_approval_and_recovery(self):
        self.run_cli('epic','create','Orders')
        self.run_cli('decision','propose','EPIC-001','Use webhook idempotency')
        self.assertIn('proposed',self.run_cli('decision','list').stdout)
        self.assertNotEqual(self.run_cli('decision','approve','1','--by','user','--evidence','',ok=False).returncode,0)
        self.run_cli('decision','approve','1','--by','user','--evidence','Approved in conversation')
        self.run_cli('approve','EPIC-001','requirements','--by','user','--evidence','Approved requirements')
        self.run_cli('checkpoint','EPIC-001','Analysis complete','--next','Create tasks')
        self.assertIn('Analysis complete',self.run_cli('recover').stdout)
        self.assertIn('APPROVATA',(self.root/'.ai/epics/EPIC-001/decisions.md').read_text())
    def test_lifecycle_guards(self):
        self.run_cli('epic','create','Orders')
        self.run_cli('task','create','EPIC-001','Import')
        self.assertNotEqual(self.run_cli('workflow-epic','finish','EPIC-001','--by','user','--evidence','yes',ok=False).returncode,0)
        for kind in ('scope','requirements','plan'):
            self.run_cli('approve','EPIC-001',kind,'--by','user','--evidence','Approved')
        self.run_cli('workflow-epic','approve','EPIC-001','--by','user','--evidence','Approved')
        self.run_cli('workflow-task','start','EPIC-001','TASK-001')
        self.run_cli('workflow-task','review','EPIC-001','TASK-001')
        self.run_cli('approve','EPIC-001/TASK-001','acceptance','--by','user','--evidence','Validated')
        self.run_cli('workflow-task','finish','EPIC-001','TASK-001','--by','user','--evidence','Validated')
        self.run_cli('workflow-epic','finish','EPIC-001','--by','user','--evidence','Validated')
        self.assertIn('completed',self.run_cli('status').stdout)
if __name__=='__main__': unittest.main()
