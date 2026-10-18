"""Sanitized Codespace-only Unity proof. Never publish Unity logs or account identity."""
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

def summarise(mode, version, code, path):
    f=Path(path)
    output={"kind":"synthetic-codespace-unity-proof", "stage":mode,
            "editor_version":version,"exit_code":code,"status":"FAIL",
            "production_repository_tested":False,"credentials_exported":False}
    if mode=="test":
        output.update({"test_report_exists":f.is_file(),"tests":0,"failures":0})
        if code==0 and f.is_file():
            try:
                root=ET.parse(f).getroot()
                count=int(root.attrib.get("total","0"))
                failed=int(root.attrib.get("failed","0"))+int(root.attrib.get("errors","0"))
                output.update({"tests":count,"failures":failed})
                if count>=4 and failed==0 and root.attrib.get("result")=="Passed":
                    output["status"]="PASS"
            except (ET.ParseError,ValueError,OSError):
                pass
    elif mode=="windows":
        output["windows_exe_exists"]=f.is_file()
        if code==0 and f.is_file() and f.stat().st_size>0:
            output["sha256"]=hashlib.sha256(f.read_bytes()).hexdigest()
            output["status"]="PASS"
    return output

if __name__=="__main__":
    if len(sys.argv)==3 and sys.argv[1]=="check":
        try:
            obj=json.loads(Path(sys.argv[2]).read_text())
            if obj.get("kind")!="synthetic-codespace-unity-proof" or obj.get("status")!="PASS":
                raise SystemExit(1)
        except (OSError,ValueError):
            raise SystemExit(1)
        raise SystemExit(0)
    if len(sys.argv)!=5 or sys.argv[1] not in ("test","windows"):
        raise SystemExit("Expected: test|windows VERSION EXIT_CODE FILE")
    print(json.dumps(summarise(sys.argv[1],sys.argv[2],int(sys.argv[3]),sys.argv[4]),sort_keys=True,indent=2))
