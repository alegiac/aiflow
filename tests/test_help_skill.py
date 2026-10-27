import unittest
from pathlib import Path
from installer import integrate

class HelpSkillTest(unittest.TestCase):
    def test_help_installed_and_triggered(self):
        skill = integrate.SKILLS / 'aiflow-help' / 'SKILL.md'
        self.assertTrue(skill.exists())
        self.assertIn('aiflow?', skill.read_text())
        self.assertIn('aiflow-help', integrate.HEADER)
        self.assertIn('sola lettura', skill.read_text())
