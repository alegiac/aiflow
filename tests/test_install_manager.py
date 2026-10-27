import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / 'tools' / 'install_manager.py'
spec = importlib.util.spec_from_file_location('aiflow_install_manager', SCRIPT)
manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manager)

class InstallManagerTests(unittest.TestCase):
    def test_valid_package(self):
        with tempfile.TemporaryDirectory() as d:
            b = io.BytesIO()
            with zipfile.ZipFile(b, 'w') as z:
                z.writestr('ai-development-framework/bin/aiflow', '#!/usr/bin/env python3\n')
                z.writestr('ai-development-framework/README.md', 'test')
            root = manager.unpack_safe(b.getvalue(), Path(d))
            self.assertTrue((root / 'bin/aiflow').is_file())
    def test_zip_traversal_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            b = io.BytesIO()
            with zipfile.ZipFile(b, 'w') as z:
                z.writestr('../escape.txt', 'bad')
                z.writestr('aiflow/bin/aiflow', 'ok')
            with self.assertRaises(RuntimeError):
                manager.unpack_safe(b.getvalue(), Path(d))

if __name__ == '__main__': unittest.main()
