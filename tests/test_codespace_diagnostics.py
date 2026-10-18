import unittest
from tools.diagnose_codespace_unity import summarize

class UnityCodespaceDiagnosticPrivacy(unittest.TestCase):
    def test_reports_missing_libraries_without_exposing_paths(self):
        secret="MY_SECRET_UNITY_PASSWORD_123"
        inp="/home/codespace/Unity/Editor/Unity: error while loading shared libraries: libGL.so.1: cannot open shared object file\n"+secret
        d=summarize(inp)
        self.assertIn("linux_dynamic_loader_problem",d["findings"])
        self.assertNotIn("/home/codespace",str(d))
        self.assertNotIn(secret,str(d))
    def test_reports_compiler_error_code_but_not_file_or_content(self):
        d=summarize("/home/private/file.cs(2,3): error CS0246: CustomerSecret Missing type")
        self.assertEqual(d["compiler_codes"],["CS0246"])
        self.assertNotIn("CustomerSecret",str(d))
        self.assertNotIn("/home/private",str(d))
    def test_reports_no_test_verdict(self):
        d=summarize("Error: Test run did not complete. Unity exited with code 6 before reporting results.")
        self.assertIn("test_runner_did_not_finish",d["findings"])
        self.assertIn("UNVERIFIED",d["test_outcome"])
    def test_authentication_tokens_never_leave_in_json(self):
        d=summarize("License error: expired token=abc123 email=someone@example.com")
        self.assertIn("licensing_or_entitlement_problem",d["findings"])
        self.assertNotIn("abc123",str(d))
        self.assertNotIn("someone@example.com",str(d))
    def test_unknown_log_still_redacted(self):
        d=summarize("PrivateFileName private-domain.tld Bearer abcdef")
        self.assertEqual({},d["findings"])
        self.assertNotIn("private-domain.tld",str(d))
