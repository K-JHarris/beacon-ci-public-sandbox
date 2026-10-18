import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class DotnetSyntheticCI(unittest.TestCase):
 def test_compiles_same_real_runtime_source(self):
  p=(ROOT/"tools/synthetic-dotnet-check/Smoke.csproj").read_text()
  self.assertIn("../../Assets/BeaconPoc/Runtime/WillMath.cs",p)
  self.assertIn("TreatWarningsAsErrors",p)
 def test_no_unity_license_needed(self):
  s=(ROOT/".github/workflows/synthetic-csharp-compile.yml").read_text()
  for x in ["UNITY_PASSWORD","UNITY_LICENSE","secrets.","unity auth","unity license", "unity install"]:
   self.assertNotIn(x,s)
  self.assertIn("persist-credentials: false",s)
 def test_overflow_and_negative_regression(self):
  s=(ROOT/"tools/synthetic-dotnet-check/Program.cs").read_text()
  self.assertIn("Overflow-safe addition",s)
  self.assertIn("ArgumentOutOfRangeException",s)
