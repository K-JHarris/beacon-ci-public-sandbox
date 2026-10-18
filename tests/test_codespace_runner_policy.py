import tempfile
import unittest
from pathlib import Path
from tools.summarize_codespace_unity import summarise

ROOT=Path(__file__).resolve().parents[1]
class CodespaceRunnerSecurity(unittest.TestCase):
 def setUp(self): self.script=(ROOT/"tools/codespace-unity-proof.sh").read_text()
 def test_codespace_and_exact_repo_only(self):
  self.assertIn('"$CODESPACES" != "true"',self.script)
  self.assertIn('K-JHarris/beacon-ci-public-sandbox',self.script)
  self.assertIn('git diff --quiet HEAD -- Assets/ Packages/ ProjectSettings/',self.script)
 def test_license_checked_without_authentication(self):
  self.assertIn('unity license status >/dev/null 2>&1',self.script)
  for bad in ["unity auth login","unity license activate","UNITY_PASSWORD","UNITY_LICENSE","UnityEntitlementLicense.xml","git push","gh secret"]:
   self.assertNotIn(bad,self.script)
 def test_actual_unity_tests_gated_by_resources(self):
  for expected in ["--mode EditMode","INSTALL_FLAGS=(--allow-install)","MIN_FREE_GIB=4","MIN_FREE_GIB=10","--execute-method Beacon.Poc.CIWindowsBuild.Build"]:
   self.assertIn(expected,self.script)
  self.assertNotIn("unity install-modules",self.script)
 def test_reuse_installed_editor_without_redownload(self):
  self.assertIn('EDITOR_BIN="$HOME/Unity/Hub/Editor/$VERSION/Editor/Unity"',self.script)
  self.assertIn('if [[ -x "$EDITOR_BIN" ]]; then',self.script)
  self.assertIn('INSTALL_FLAGS=()',self.script)
  self.assertIn('"${INSTALL_FLAGS[@]}"',self.script)
  self.assertIn('for MOUNT in "$ROOT" "$HOME"; do',self.script)
  self.assertIn('MISSING_LIBS=',self.script)
 def test_nunit_pass_must_contain_four_tests(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"result.xml"
   p.write_text('<test-run total="4" passed="4" failed="0" result="Passed"/>')
   self.assertEqual("PASS",summarise("test","6000.6.5f1",0,p)["status"])
   p.write_text('<test-run total="0" result="Passed"/>')
   self.assertEqual("FAIL",summarise("test","6000.6.5f1",0,p)["status"])
   p.write_text('<test-run total="4" failed="1" result="Failed"/>')
   self.assertEqual("FAIL",summarise("test","6000.6.5f1",8,p)["status"])
   p.write_text("not xml")
   self.assertEqual("FAIL",summarise("test","6000.6.5f1",0,p)["status"])
 def test_no_windows_pass_without_binary(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"Game.exe"
   self.assertEqual("FAIL",summarise("windows","6000.6.5f1",0,p)["status"])
   p.write_bytes(b"unit fixture")
   self.assertEqual("PASS",summarise("windows","6000.6.5f1",0,p)["status"])
