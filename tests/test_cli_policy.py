"""Fail closed if the discovery workflow starts requiring credentials or activation."""
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
class CliDiscoverySafety(unittest.TestCase):
    def setUp(self):
        self.wf = (ROOT / ".github/workflows/unity-cli-discovery.yml").read_text()
    def test_no_secret_exposure(self):
        self.assertNotIn("secrets.", self.wf)
        self.assertNotIn("UNITY_PASSWORD", self.wf)
        self.assertNotIn("UNITY_LICENSE", self.wf)
        self.assertNotIn("UNITY_SERVICE_ACCOUNT_SECRET", self.wf)
    def test_no_license_activation(self):
        self.assertIn("unity license activate --help", self.wf)
        self.assertNotIn("unity license activate --personal", self.wf)
        self.assertNotIn("unity auth login", self.wf)
        self.assertNotIn("unity install 6000", self.wf)
    def test_discovery_is_manual_only(self):
        self.assertIn("workflow_dispatch: {}", self.wf)
        self.assertNotIn("  push:", self.wf)
    def test_safe_remote_only(self):
        self.assertIn("runs-on: ubuntu-24.04", self.wf)
        self.assertIn("persist-credentials: false", self.wf)
        self.assertIn("contents: read", self.wf)
        self.assertIn("UNITY_NO_CLOUD", self.wf)
    def test_result_report_explicit_limits(self):
        s = (ROOT / "tools/verify_unity_cli_discovery.py").read_text()
        for flag in ["auth_login_performed", "license_activation_attempted", "unity_editor_installed", "windows_build_executed"]:
            self.assertIn('"'+flag+'": False', s)
