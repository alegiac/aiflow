import os
from pathlib import Path
import subprocess
import tempfile
import unittest

CLI=Path(__file__).resolve().parents[1]/'bin'/'aiflow'

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
    def run_cli(self,*args,ok=True):
        env=os.environ.copy(); env['AIFLOW_PROJECT']=str(self.root)
        p=subprocess.run([str(CLI),*args],env=env,text=True,capture_output=True)
        if ok: self.assertEqual(p.returncode,0,p.stderr)
        return p
    def test_workflow(self):
        self.run_cli('init','--name','Demo')
        self.run_cli('epic','create','Users')
        self.run_cli('epic','create','Other')
        self.run_cli('task','create','EPIC-001','Login')
        self.run_cli('task','create','EPIC-001','Roles')
        self.run_cli('task','create','EPIC-002','Import')
        self.assertTrue((self.root/'.ai/epics/EPIC-001/tasks/TASK-001/task.md').exists())
        self.assertTrue((self.root/'.ai/epics/EPIC-001/tasks/TASK-001/report.md').exists())
        self.assertIn('EPIC-002',self.run_cli('status').stdout)
        self.run_cli('session','start')
        self.run_cli('track','start','--epic','EPIC-001','--task','TASK-001')
        self.run_cli('track','stop')
        self.run_cli('session','stop')
        self.run_cli('export',str(self.root/'tracking.csv'))
        self.assertIn('duration_minutes',(self.root/'tracking.csv').read_text())
    def test_custom_ids_and_approval_guard(self):
        self.run_cli('init')
        self.run_cli('epic','create','Custom','--id','AUTH')
        self.assertNotEqual(self.run_cli('epic','create','Duplicate','--id','AUTH',ok=False).returncode,0)
        self.assertNotEqual(self.run_cli('epic','status','AUTH','approved',ok=False).returncode,0)
        for kind in ('scope','requirements','plan'):
            self.run_cli('approve','AUTH',kind,'--by','user','--evidence','Explicit approval')
        self.run_cli('workflow-epic','approve','AUTH','--by','user','--evidence','Explicit approval')
        self.assertIn('Stato: approved',(self.root/'.ai/epics/AUTH/epic.md').read_text())
    def test_multiple_profiles_and_incremental_changes(self):
        import json
        self.run_cli('init', '--profile', 'php-laravel,react,shadcn,shopify-graphql,mysql')
        cfg = self.root / '.ai/config.json'
        data = json.loads(cfg.read_text())
        self.assertEqual(data['profiles'], ['php-laravel', 'react', 'shadcn', 'shopify-graphql', 'mysql'])
        self.assertIn('react', (self.root / '.ai/profiles/README.md').read_text())
        self.run_cli('profile', 'add', 'nodejs,react')
        self.assertEqual(json.loads(cfg.read_text())['profiles'][-1], 'nodejs')
        self.run_cli('profile', 'remove', 'mysql')
        self.assertNotIn('mysql', json.loads(cfg.read_text())['profiles'])
        self.run_cli('profile', 'sync')
        self.assertIn('nodejs', self.run_cli('profile', 'list').stdout)
        self.assertIn('postgresql', self.run_cli('profile', 'available').stdout)

    def test_profile_walkthrough_is_read_only_and_available_outside_project(self):
        for slug in ('php-laravel', 'react', 'shadcn', 'tailwind', 'shopify-rest',
                     'shopify-graphql', 'postgresql', 'mysql', 'nodejs'):
            result = self.run_cli('profile', 'walkthrough', slug)
            self.assertIn('AIFlow profile walkthrough:', result.stdout)
            self.assertIn('##', result.stdout)
        self.assertFalse((self.root / '.ai').exists())
        bad = self.run_cli('profile', 'walkthrough', 'unknown', ok=False)
        self.assertNotEqual(bad.returncode, 0)

    def test_unknown_profile_and_existing_project_preservation(self):
        import json
        bad = self.run_cli('init', '--profile', 'not-a-real-profile', ok=False)
        self.assertNotEqual(bad.returncode, 0)
        self.run_cli('init', '--profile', 'php-laravel')
        self.run_cli('profile', 'add', 'react')
        self.run_cli('init', '--profile', 'php-laravel')
        self.assertEqual(json.loads((self.root / '.ai/config.json').read_text())['profiles'], ['php-laravel', 'react'])
        bad = self.run_cli('profile', 'add', 'not-a-real-profile', ok=False)
        self.assertNotEqual(bad.returncode, 0)
        self.assertEqual(json.loads((self.root / '.ai/config.json').read_text())['profiles'], ['php-laravel', 'react'])

    def test_does_not_overwrite(self):
        self.run_cli('init')
        path=self.root/'.ai/project.md'; path.write_text('Personalizzato')
        self.run_cli('init')
        self.assertEqual(path.read_text(),'Personalizzato')

if __name__=='__main__': unittest.main()
