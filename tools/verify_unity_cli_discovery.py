"""CLI help inspection only; never authenticate, activate, or launch the Unity Editor."""
import json
from pathlib import Path
import sys

root = Path(sys.argv[1])
cli = (root / "cli-help.txt").read_text()
auth = (root / "auth-help.txt").read_text()
license_help = (root / "license-help.txt").read_text()
activate_help = (root / "license-activate-help.txt").read_text()
test_help = (root / "test-help.txt").read_text()
version = (root / "version.txt").read_text().strip()

flags = {
    "auth_command": "login" in auth or "login" in cli,
    "license_command": "activate" in license_help,
    "personal_mode": "--personal" in activate_help,
    "eula_flag": "--accept-eula" in activate_help,
    "test_command": "test" in cli or "--" in test_help,
}
report = {
    "kind": "credential-free-unity-cli-discovery",
    "cli_version": version,
    "checks": flags,
    "auth_login_performed": False,
    "license_activation_attempted": False,
    "unity_editor_installed": False,
    "unity_tests_executed": False,
    "windows_build_executed": False,
    "license_compatibility": "Not established by a help-only smoke test",
}
(root / "discovery.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
print(json.dumps(report, sort_keys=True))
if not all(flags.values()):
    print("One or more expected CLI capabilities are absent; inspect CLI version/help.", file=sys.stderr)
    raise SystemExit(1)
