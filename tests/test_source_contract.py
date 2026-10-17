import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class SourceTests(unittest.TestCase):
    def test_unity_version(self): self.assertIn("6000.6.5f1",(ROOT/"ProjectSettings/ProjectVersion.txt").read_text())
    def test_framework(self): self.assertIn("com.unity.test-framework",json.loads((ROOT/"Packages/manifest.json").read_text())["dependencies"])
    def test_overflow_fix(self): self.assertIn("(long)current + gain",(ROOT/"Assets/BeaconPoc/Runtime/WillMath.cs").read_text())
    def test_no_beacon_production(self): self.assertFalse((ROOT/"Assets/Beacon").exists())
