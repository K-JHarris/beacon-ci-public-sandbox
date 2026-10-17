import hashlib,json,os
from pathlib import Path
root=Path(__file__).resolve().parents[1]
paths=["ProjectSettings/ProjectVersion.txt","Packages/manifest.json","Assets/BeaconPoc/Runtime/WillMath.cs",".github/workflows/unity-proof.yml"]
print(json.dumps({"kind":"synthetic-public-ci-static-proof","unity_not_executed":True,"github_sha":os.getenv("GITHUB_SHA","LOCAL"),"files":{p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}},sort_keys=True,indent=2))
