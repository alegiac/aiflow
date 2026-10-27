import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

CLI=Path(__file__).resolve().parents[1]/'bin/aiflow'

class IntegrationTests(unittest.TestCase):
    def run_cli(self,root,*args):
        result=subprocess.run([str(CLI),*args],cwd=root,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        return result.stdout

    def test_both_and_idempotence(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/'AGENTS.md').write_text('Custom codex rules\n')
            (root/'CLAUDE.md').write_text('Custom claude rules\n')
            self.run_cli(root,'init')
            self.run_cli(root,'integrate','both')
            self.run_cli(root,'integrate','both')
            for file,original in [('AGENTS.md','Custom codex rules'),('CLAUDE.md','Custom claude rules')]:
                content=(root/file).read_text()
                self.assertIn(original,content)
                self.assertEqual(content.count('<!-- AIFLOW:START -->'),1)
            self.assertTrue((root/'.agents/skills/aiflow-analitica/SKILL.md').exists())
            self.assertTrue((root/'.claude/skills/aiflow-end-task/SKILL.md').exists())
            self.assertTrue((root/'.claude/agents/aiflow-code-reviewer.md').exists())
            self.assertEqual(json.loads((root/'.ai/config.json').read_text())['integrations'],['claude','codex'])
