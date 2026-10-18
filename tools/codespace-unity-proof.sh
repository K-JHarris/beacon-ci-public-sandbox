#!/usr/bin/env bash
# Codespace-only, licensed synthetic Unity Editor verification.
# Never logs in, reads credentials, transfers activation, or commits private data.
set -Eeuo pipefail
export UNITY_NO_PAGER=1 UNITY_NON_INTERACTIVE=1
ACTION="$1"
case "$ACTION" in preflight|test|windows) ;; *) echo "Usage: bash tools/codespace-unity-proof.sh [preflight|test|windows]"; exit 2;; esac
if [[ "$CODESPACES" != "true" ]]; then
  echo "STOP: use your licensed GitHub Codespace, not your PC or a public Actions runner."; exit 3
fi
command -v unity >/dev/null || { echo "STOP: Unity CLI unavailable."; exit 4; }
command -v python3 >/dev/null || { echo "STOP: Python3 unavailable."; exit 4; }
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
ORIGIN="$(git remote get-url origin 2>/dev/null || true)"
if [[ ! "$ORIGIN" =~ github\.com[:/]K-JHarris/beacon-ci-public-sandbox(\.git)?$ ]]; then
  echo "STOP: wrong repository. Only the public synthetic sandbox is permitted."; exit 5
fi
if ! git diff --quiet HEAD -- Assets/ Packages/ ProjectSettings/; then
  echo "STOP: tracked synthetic Unity files are modified; preserve changes before running."; exit 5
fi
VERSION="$(sed -n 's/^m_EditorVersion: //p' ProjectSettings/ProjectVersion.txt | head -n 1)"
if [[ ! "$VERSION" =~ ^6000\.[0-9]+\.[0-9]+f[0-9]+$ ]]; then
  echo "STOP: unrecognized synthetic Unity Editor version."; exit 5
fi
mkdir -p results
CLI_VERSION="$(unity --version 2>/dev/null || true)"
if [[ -z "$CLI_VERSION" ]]; then echo "STOP: Unity CLI unresponsive."; exit 6; fi
if ! unity license status >/dev/null 2>&1; then
  echo "STOP: active license not verified in this Codespace; no login attempted."; exit 7
fi
if ! unity projects verify "$ROOT" > results/codespace-verify-private.log 2>&1; then
  echo "STOP: Unity project integrity failed; private details stay in ignored results/."; exit 8
fi
echo "PASS: licensed Codespace, synthetic project, and CLI $CLI_VERSION (Editor $VERSION)."
if [[ "$ACTION" == preflight ]]; then
  echo "READY: after checking free Codespaces quota, run: bash tools/codespace-unity-proof.sh test"
  echo "Note: this can install a multi-GB Editor, consuming Codespaces minutes/storage."
  exit 0
fi
if [[ "$ACTION" == test ]]; then
  FREE_KB="$(df -Pk "$ROOT" | awk 'END {print $4}')"
  if [[ ! "$FREE_KB" =~ ^[0-9]+$ ]] || (( FREE_KB < 10 * 1024 * 1024 )); then
    echo "STOP: less than 10GiB free; no Editor download attempted."; exit 9
  fi
  echo "Starting actual Unity Edit Mode tests using your active Codespace license."
  OUTPUT="results/codespace-editmode.xml"
  rm -f "$OUTPUT"
  set +e
  timeout 2700 unity test "$ROOT" --mode EditMode --editor-version "$VERSION" --allow-install --timeout 2400 --output "$OUTPUT" -- -nographics > results/codespace-editor-private.log 2>&1
  CODE=$?
  set -e
  python3 tools/summarize_codespace_unity.py test "$VERSION" "$CODE" "$OUTPUT" > results/codespace-editmode-summary.json
  cat results/codespace-editmode-summary.json
  if ! python3 tools/summarize_codespace_unity.py check results/codespace-editmode-summary.json; then
    echo "STOP: native Unity tests did not pass. Raw log remains only in ignored results/."; exit 10
  fi
  if ! git diff --quiet HEAD -- Assets/ Packages/ ProjectSettings/; then
    echo "STOP: Editor modified tracked project inputs; no automatic reset."; exit 11
  fi
  echo "PASS: actual synthetic Unity Editor tests; Windows is a separate stage."
  exit 0
fi
if [[ "$ACTION" == windows ]]; then
  if [[ ! -f results/codespace-editmode-summary.json ]] || ! python3 tools/summarize_codespace_unity.py check results/codespace-editmode-summary.json >/dev/null; then
    echo "STOP: an actual Editor test PASS must precede Windows build."; exit 12
  fi
  mkdir -p build/StandaloneWindows64
  OUTPUT="build/StandaloneWindows64/BeaconPoc.exe"
  echo "Attempting Windows Mono build with existing installed modules; no auto-install."
  set +e
  timeout 2700 unity build "$ROOT" --target StandaloneWindows64 --execute-method Beacon.Poc.CIWindowsBuild.Build --output-path "$OUTPUT" --timeout 2400 > results/codespace-windows-private.log 2>&1
  CODE=$?
  set -e
  python3 tools/summarize_codespace_unity.py windows "$VERSION" "$CODE" "$OUTPUT" > results/codespace-windows-summary.json
  cat results/codespace-windows-summary.json
  if ! python3 tools/summarize_codespace_unity.py check results/codespace-windows-summary.json; then
    echo "STOP: Windows build failed or required module is missing; no modules installed."; exit 13
  fi
  echo "PASS: synthetic Windows exe built in ignored build/."
fi
