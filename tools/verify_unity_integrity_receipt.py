"""Read actual tool logs and publish a sanitized, non-sensitive proof receipt."""
import json, sys
from pathlib import Path
root=Path(sys.argv[1])
negative_exit=int(sys.argv[2])
baseline=(root/"baseline-check.txt").read_text()
negative=(root/"missing-meta-check.txt").read_text()
repaired=(root/"repaired-check.txt").read_text()
checks={
 "baseline_pass": (root/"baseline-exit0").exists(),
 "missing_meta_detected": "META_MISSING" in negative and "WillMath.cs" in negative and negative_exit!=0,
 "restored_pass": (root/"restored-exit0").exists(),
 "official_cli_version_recorded": bool((root/"version.txt").read_text().strip()),
}
receipt={
 "kind":"synthetic-unity-cli-project-integrity",
 "status":"PASS" if all(checks.values()) else "FAIL",
 "checks":checks,
 "negative_exit_code":negative_exit,
 "cli_version":(root/"version.txt").read_text().strip(),
 "editor_installed":False,
 "license_activated":False,
 "real_unity_compile":False,
 "windows_build":False,
 "private_project_access":False
}
(root/"integrity-receipt.json").write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
print(json.dumps(receipt,sort_keys=True))
if not all(checks.values()): raise SystemExit(1)
