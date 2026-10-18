import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class IntegrityWorkflowPolicy(unittest.TestCase):
 def setUp(self):
  self.workflow=(ROOT/".github/workflows/unity-cli-project-integrity.yml").read_text()
 def test_no_auth_and_no_license(self):
  for prohibited in ["secrets.", "unity auth login", "unity license activate", "UNITY_PASSWORD", "UNITY_SERVICE_ACCOUNT_SECRET", "unity install 6000"]:
   self.assertNotIn(prohibited,self.workflow)
 def test_only_synthetic_project(self):
  self.assertIn("unity projects verify .",self.workflow)
  self.assertIn("META_MISSING",self.workflow)
  self.assertIn("git diff --exit-code -- Assets/",self.workflow)
  self.assertIn("persist-credentials: false",self.workflow)
 def test_receipt_reports_no_editor_and_license(self):
  src=(ROOT/"tools/verify_unity_integrity_receipt.py").read_text()
  for key in ["editor_installed","license_activated","real_unity_compile","windows_build","private_project_access"]:
   self.assertIn('"'+key+'":False',src)
 def test_asset_meta_is_present_and_guid_unique(self):
  paths=[ROOT/"Assets/BeaconPoc/Runtime/WillMath.cs",ROOT/"Assets/BeaconPoc/Editor/CIWindowsBuild.cs",ROOT/"Assets/BeaconPoc/Tests/Editor/WillMathTests.cs"]
  for path in paths:
   self.assertTrue(path.with_name(path.name+".meta").exists(),str(path))
  metas=list((ROOT/"Assets").rglob("*.meta"))
  guids=[next((l.split(":",1)[1].strip() for l in m.read_text().splitlines() if l.startswith("guid:")),None) for m in metas]
  self.assertEqual(len(guids),len(set(guids)))
  self.assertNotIn(None,guids)
