import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('validate_profiles',ROOT/'tools/validate_profiles.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class ProfileTests(unittest.TestCase):
    def test_existing_profiles(self):
        self.assertEqual([],module.validate(ROOT))
    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'profiles'/'python-django').mkdir(parents=True)
            self.assertTrue(any('manca PROFILE.md' in x for x in module.validate(root)))
if __name__=='__main__':unittest.main()
