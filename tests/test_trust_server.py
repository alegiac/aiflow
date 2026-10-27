import tempfile
import unittest
from pathlib import Path
from installer.integrate import install

class TrustServerTests(unittest.TestCase):
    def test_install_both_and_preserve_existing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'.aiflow').mkdir()
            (root/'.aiflow/config.json').write_text('{}')
            install(root,'both')
            for path in (root/'.agents/skills/aiflow-trust-server/SKILL.md',root/'.claude/skills/aiflow-trust-server/SKILL.md'):
                self.assertTrue(path.exists())
                self.assertIn('autorizzazione esplicita',path.read_text())
            codex=root/'.agents/skills/aiflow-trust-server/SKILL.md'
            codex.write_text('my original custom skill')
            install(root,'codex')
            self.assertEqual(codex.read_text(),'my original custom skill')

if __name__=='__main__': unittest.main()
