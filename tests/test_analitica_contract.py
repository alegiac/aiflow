import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class AnaliticaContractTests(unittest.TestCase):
    def test_skill_requires_wait_after_question(self):
        content = (ROOT / 'core/skills/analitica/SKILL.md').read_text()
        self.assertIn('ASK → STOP → WAIT', content)
        self.assertIn('termina il turno immediatamente', content)
        self.assertIn('ultima domanda rimasta senza risposta', content)

    def test_installer_instructions_include_wait_rule(self):
        content = (ROOT / 'installer/integrate.py').read_text()
        self.assertIn('STOP the turn and WAIT', content)

if __name__ == '__main__':
    unittest.main()
