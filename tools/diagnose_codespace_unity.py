"""Diagnose a local Unity Codespaces run without exporting raw logs or credentials.

Reads ignored results/codespace-editor-private.log and prints only fixed categories,
public diagnostic codes, and counts. Does not print matched source lines, user
paths, email addresses, keys, tokens, URLs, or Unity license details.
"""
from collections import Counter
from pathlib import Path
import json
import re

LOG = Path("results/codespace-editor-private.log")
RULES = {
    "editor_missing_linux_library": r"(?:error while loading shared libraries|lib[A-Za-z0-9+_.-]+\.so(?:\.\d+)*\s*=>\s*not found)",
    "graphics_or_display_unavailable": r"(?:cannot open display|failed to open.*display|no display|X11.*(?:fail|error)|Xvfb|DISPLAY.*(?:unset|missing|not set)|failed to initialize graphics|libGL\.so)",
    "licensing_or_entitlement_problem": r"(?:license|licensing|entitlement|activation).{0,100}(?:fail|error|expired|invalid|unavailable|denied|refused)|(?:fail|error|expired|invalid).{0,100}(?:license|licensing|entitlement|activation)",
    "package_resolution_problem": r"(?:package\s*manager|resolving packages|resolve package|com\.unity\.[a-z0-9_.-]+).{0,120}(?:fail|error|not found|timeout|unable)|(?:fail|error).{0,120}(?:package\s*manager|resolving packages)",
    "csharp_compiler_error": r"\berror\s+CS\d{4}\b",
    "linux_dynamic_loader_problem": r"(?:GLIBC_[0-9.]+\s+not found|symbol lookup error|error while loading shared libraries|cannot open shared object file)",
    "disk_or_memory_exhaustion": r"(?:No space left on device|disk full|not enough disk|out of memory|cannot allocate memory|OOM killed)",
    "editor_crash_or_signal": r"(?:SIGSEGV|segmentation fault|Editor.*(?:crashed|terminated by signal)|signal\s+(?:6|9|11)|core dumped|abort trap)",
    "permissions_problem": r"(?:permission denied|access denied)",
    "run_timeout": r"(?:timeout|timed out|deadline exceeded)",
    "test_runner_did_not_finish": r"(?:test run did not complete|Unity exited with code [1-9]|no test results|no test report)",
}
PUBLIC_CODES = re.compile(r"\berror\s+(CS\d{4})\b", re.IGNORECASE)
def summarize(log: str):
    counts = Counter()
    codes = set()
    for line in log.splitlines():
        for name, regex in RULES.items():
            if re.search(regex, line, re.IGNORECASE):
                counts[name] += 1
        for code in PUBLIC_CODES.findall(line):
            codes.add(code.upper())
    return {
        "source": "ignored local Codespace Unity CLI log",
        "privacy": "categories and compiler codes only; no raw lines or credentials",
        "log_lines": len(log.splitlines()),
        "findings": dict(sorted(counts.items())),
        "compiler_codes": sorted(codes)[:20],
        "test_outcome": "UNVERIFIED — Unity CLI exited 6 without an NUnit report",
    }

if __name__ == "__main__":
    if not LOG.is_file():
        raise SystemExit("STOP: no local Unity test log at results/codespace-editor-private.log")
    print(json.dumps(summarize(LOG.read_text(encoding="utf-8", errors="replace")), sort_keys=True, indent=2))
