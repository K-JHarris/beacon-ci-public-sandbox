"""Source-only Unity Build Automation scene contract; native Editor is still required."""
import re
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SCENE = "Assets/BeaconPoc/Scenes/SmokeScene.unity"

class BuildSceneContract(unittest.TestCase):
    def test_scene_exists_and_meta_guid_is_in_build_settings(self):
        scene = ROOT / SCENE
        meta = ROOT / (SCENE + ".meta")
        settings = ROOT / "ProjectSettings/EditorBuildSettings.asset"
        self.assertTrue(scene.is_file())
        self.assertTrue(meta.is_file())
        self.assertTrue(settings.is_file())
        guid = re.search(r"(?m)^guid: ([0-9a-f]{32})$", meta.read_text())
        self.assertIsNotNone(guid)
        settings_text = settings.read_text()
        self.assertIn("path: " + SCENE, settings_text)
        self.assertIn("guid: " + guid.group(1), settings_text)
        self.assertIn("enabled: 1", settings_text)

    def test_synthetic_play_mode_fixture_has_own_test_assembly(self):
        root = ROOT / "Assets/BeaconPoc/Tests/PlayMode"
        self.assertTrue((root / "Beacon.Poc.Tests.PlayMode.asmdef.meta").is_file())
        asmdef = (root / "Beacon.Poc.Tests.PlayMode.asmdef").read_text()
        self.assertIn("TestAssemblies", asmdef)
        test = (root / "WillMathPlayModeTests.cs").read_text()
        self.assertIn("[UnityTest]", test)
        self.assertIn("yield return null;", test)
        self.assertIn("(int.MaxValue - 1, int.MaxValue, int.MaxValue)", test)
