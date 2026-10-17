import tempfile, unittest
from pathlib import Path
from tools.public_safety_gate import inspect
class SafetyTests(unittest.TestCase):
    def test_empty(self):
        with tempfile.TemporaryDirectory() as d: self.assertFalse(inspect(Path(d)))
    def test_env_is_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d)/".env.production").write_text("fake")
            self.assertTrue(inspect(Path(d)))
    def test_fake_email_is_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d)/"profile.txt").write_text("sample.user@gmail.com")
            self.assertTrue(inspect(Path(d)))
    def test_fake_token_is_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d)/"token.txt").write_text("ghp_" + "X"*24)
            self.assertTrue(inspect(Path(d)))
