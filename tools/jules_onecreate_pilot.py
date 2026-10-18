#!/usr/bin/env python3
"""One approved Jules session, synthetic public repo only. Not a production dispatcher.

One irreversible attempt: after an atomic GitHub ref reservation, Jules POST is
issued once with no automatic retries. A timeout permanently blocks rerun until
an owner audits Jules sessions and the GitHub reservation.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

REPO = "K-JHarris/beacon-ci-public-sandbox"
PILOT_REF = "refs/heads/pilot/jules-overflow-20261018"
PILOT_BASE = "b074a27e7acf0f168e1270d41169c0d40d2bcfc9"
RESERVATION_REF = "refs/heads/pilot/jules-dispatch-reservation-20261018"
API_GH = "https://api.github.com/repos/" + REPO
API_JULES = "https://jules.googleapis.com/v1alpha"
CONFIRM = "RUN_ONE_FREE_JULES_SANDBOX_PILOT"


def request(method, url, *, headers, body=None):
    if body is not None:
        data = json.dumps(body, separators=(",", ":")).encode("utf-8")
    else:
        data = None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    # Do not print HTTP response bodies (may contain private details).
    with urllib.request.urlopen(req, timeout=30) as response:
        result = response.read(2_000_000)
        return json.loads(result) if result else {}


def only_source(jules_headers):
    found = []
    next_page = ""
    for _ in range(10):
        params = urllib.parse.urlencode({"pageSize": 100, **({"pageToken": next_page} if next_page else {})})
        reply = request("GET", API_JULES + "/sources?" + params, headers=jules_headers)
        for source in reply.get("sources", []):
            repo = source.get("githubRepo") or {}
            if (str(repo.get("owner", "")).casefold() == "k-jharris" and
                    str(repo.get("repo", "")).casefold() == "beacon-ci-public-sandbox" and
                    str(source.get("name", "")).startswith("sources/github/")):
                found.append(source["name"])
        next_page = reply.get("nextPageToken", "")
        if not next_page:
            break
    else:
        raise RuntimeError("Source pagination exceeded safe limit")
    if len(set(found)) != 1:
        raise RuntimeError("Jules sandbox source absent or ambiguous; no session created")
    return found[0]


def main():
    env = os.environ
    if (env.get("GITHUB_REPOSITORY") != REPO or
            env.get("GITHUB_ACTOR", "").casefold() != "k-jharris" or
            env.get("GITHUB_REF") != "refs/heads/main" or
            env.get("GITHUB_EVENT_NAME") != "workflow_dispatch" or
            env.get("GITHUB_RUN_ATTEMPT") != "1" or
            env.get("PILOT_CONFIRM") != CONFIRM):
        raise RuntimeError("Unapproved repository, actor, main ref, run or confirmation")
    gh_token = env.get("GH_TOKEN")
    key = env.get("JULES_API_KEY")
    if not gh_token or not key:
        raise RuntimeError("Sandbox-only encrypted key/token missing; no reservation")
    gh_headers = {"Authorization": "Bearer " + gh_token,
                  "Accept": "application/vnd.github+json",
                  "X-GitHub-Api-Version": "2022-11-28",
                  "Content-Type": "application/json",
                  "User-Agent": "BEACON-Synthetic-OneCreate-Pilot"}
    jules_headers = {"X-Goog-Api-Key": key,
                     "Accept": "application/json",
                     "Content-Type": "application/json",
                     "User-Agent": "BEACON-Synthetic-OneCreate-Pilot"}
    # No network mutation until the exact pinned source and connection are checked.
    base = request("GET", API_GH + "/git/ref/" + PILOT_REF.removeprefix("refs/"), headers=gh_headers)
    if base.get("object", {}).get("sha") != PILOT_BASE:
        raise RuntimeError("Isolated synthetic base changed; refuse to launch")
    source = only_source(jules_headers)
    print("PRECHECK_OK: exact public sandbox source and pinned branch; no production source")
    # GitHub git/ref creation is atomic. Never automatically delete the
    # unique reservation on failures or uncertain POST outcomes.
    try:
        request("POST", API_GH + "/git/refs", headers=gh_headers,
                body={"ref": RESERVATION_REF, "sha": PILOT_BASE})
    except urllib.error.HTTPError as e:
        raise RuntimeError("Pilot reservation failed (possibly already reserved): " + str(e.code)) from None
    except Exception:
        raise RuntimeError("Reservation outcome unknown; halt and inspect GitHub before any retry") from None
    print("SINGLE_CREATE_RESERVED: permanent ref written; reruns prohibited")
    payload = {
        "title": "BEACON public synthetic overflow safety pilot",
        "prompt": ("PUBLIC SYNTHETIC TEST ONLY. Starting branch pilot/jules-overflow-20261018 "
                   "contains an intentional overflow bug. Change ONLY "
                   "Assets/BeaconPoc/Runtime/WillMath.cs to restore overflow-safe int addition. "
                   "Do not alter tests, workflows, configuration, .meta files, policies, "
                   "GitHub settings, or any other file. Do not merge the PR. "
                   "Preserve negative-input rejection and capacity clamping. "
                   "The existing tools/synthetic-dotnet-check/Program.cs has an independent "
                   "overflow test; make it pass without altering that test. "
                   "Do not claim a Unity Editor or Windows executable test was run."),
        "sourceContext": {"source": source,
                          "githubRepoContext": {"startingBranch": "pilot/jules-overflow-20261018"}},
        "requirePlanApproval": True,
        "automationMode": "AUTO_CREATE_PR",
    }
    try:
        response = request("POST", API_JULES + "/sessions", headers=jules_headers, body=payload)
    except urllib.error.HTTPError as e:
        print("JULES_POST_FAILED: HTTP " + str(e.code) + " (reservation remains; NO RETRY)")
        raise SystemExit(1)
    except Exception:
        print("JULES_POST_OUTCOME_UNKNOWN: reservation remains; NO RETRY; manually reconcile Jules sessions")
        raise SystemExit(1)
    session = response.get("name", "")
    if not re.fullmatch(r"sessions/[a-zA-Z0-9_-]+", session):
        print("JULES_POST_RESPONSE_UNVERIFIED: reservation remains; do not retry")
        raise SystemExit(1)
    print("ONE_JULES_SESSION_CREATED: " + session)
    print("PLAN_REVIEW_REQUIRED: approve only the exact synthetic WillMath change in Jules UI")
    print("PR_REVIEW_REQUIRED: verify independent red/green status; never auto-merge")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, urllib.error.HTTPError, urllib.error.URLError) as err:
        print("SAFE_STOP: " + str(err).split("?")[0], file=sys.stderr)
        raise SystemExit(1)
