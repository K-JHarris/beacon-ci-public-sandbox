"""Illustrative working-tree safety test, NOT a repository-history or secret audit."""
from pathlib import Path
import re, sys
BLOCK_PATH=[re.compile(r"(^|/)(?:\.env(?:\..*)?|.*\.ulf|.*\.pem|id_rsa|id_ed25519)$",re.I),re.compile(r"(^|/)(?:Library|UserSettings|Private|Secrets|ArtRecovery)/",re.I)]
BLOCK_TEXT=[re.compile(r"ghp_[A-Za-z0-9]{20,}"),re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),re.compile(r"AIza[A-Za-z0-9_-]{25,}"),re.compile(r"AKIA[A-Z0-9]{16}"),re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),re.compile(r"[A-Za-z]:\\Users\\[A-Za-z0-9_. -]+\\",re.I),re.compile(r"[A-Za-z0-9._%+-]+@(?:gmail|yahoo|hotmail|outlook)\.com\b",re.I)]
TEXT={".py",".cs",".json",".md",".yml",".yaml",".txt",".asmdef",".gitignore"}
def inspect(root):
    failures=[]
    for f in root.rglob("*"):
        if not f.is_file() or ".git" in f.parts: continue
        rel=f.relative_to(root).as_posix()
        if rel.startswith("evidence/") or rel.endswith(".zip"): failures.append("Forbidden archive/evidence: "+rel)
        if any(p.search(rel) for p in BLOCK_PATH): failures.append("Forbidden path: "+rel)
        if f.stat().st_size > 2_000_000: failures.append("Unexpected large file: "+rel)
        if f.suffix.lower() in TEXT or f.name==".gitignore":
            try:
                content=f.read_text(encoding="utf-8")
                if rel not in {"tools/public_safety_gate.py","tests/test_security_gate.py"}:
                    for pattern in BLOCK_TEXT:
                        if pattern.search(content): failures.append("Sensitive-looking content: "+rel)
            except UnicodeError: failures.append("Non-UTF8 text: "+rel)
    return failures
if __name__=="__main__":
    issues=inspect(Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve())
    if issues:
        for i in issues: print(i,file=sys.stderr)
        raise SystemExit(1)
    print("PASS: synthetic public working-tree policy (not history scan)")
