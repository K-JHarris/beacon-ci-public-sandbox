"""Inert, public synthetic Jules issue-to-PR feasibility contract.

This module performs NO HTTP, no GitHub writes and no inference. Its sole purpose
is to fail closed on malformed, unauthorized, or empty-result simulated events.
Never run it against the owner's private game repository.
"""
from dataclasses import dataclass
import json
import re

REPO="K-JHarris/beacon-ci-public-sandbox"
OWNER="K-JHarris"
SOURCE="sources/github/K-JHarris/beacon-ci-public-sandbox"
LABEL="integration-approved"
TASK="SYNTHETIC_WILL_OVERFLOW_FIX"
ALLOWED_PATH="Assets/BeaconPoc/Runtime/WillMath.cs"
MAX_BODY_CHARS=4500

class Reject(ValueError):
    """Unsafe or unsupported synthetic request/result."""

def _need(cond: bool, reason: str):
    if not cond:
        raise Reject(reason)

def make_request(event: dict) -> dict:
    """Build a safe Jules REST session body, *without sending it anywhere*."""
    repo=event.get("repository") or {}
    actor=event.get("sender") or {}
    issue=event.get("issue") or {}
    issue_author=issue.get("user") or {}
    labels=issue.get("labels") or []
    labelnames={v.get("name") for v in labels if isinstance(v,dict)}
    body=issue.get("body") or ""
    number=issue.get("number")
    _need(repo.get("full_name")==REPO,"wrong repository")
    _need(actor.get("login")==OWNER and issue_author.get("login")==OWNER,"unapproved actor or author")
    _need(event.get("action")=="labeled","requires labeled event (no comment injection)")
    _need(LABEL in labelnames,"missing owner-only integration approval label")
    _need(isinstance(number,int) and 0<number<1000000,"invalid issue number")
    _need(isinstance(body,str) and len(body)<=MAX_BODY_CHARS,"missing or oversized task")
    _need(re.search(r"(?m)^TASK: "+TASK+r"$",body) is not None,"non-synthetic task rejected")
    _need(re.search(r"(?m)^ACCEPTANCE: Fix overflow without disabling tests$",body) is not None,
          "missing exact acceptance scope")
    _need(re.search(r"(?m)^FORBIDDEN: Policy, test and workflow changes$",body) is not None,
          "missing protected-file policy")
    prompt=(
        "PUBLIC SYNTHETIC PILOT ONLY. Work only on "+ALLOWED_PATH+
        ". Restore overflow-safe behavior without altering tests, CI or AGENTS.md. "+
        "Keep Unity .meta GUID/asmdefs intact. Provide a substantive PR with the code fix. "+
        "Do not claim Unity Editor or Windows acceptance from static tests. "+
        "The issue is #"+str(number)+"."
    )
    return {
        "title":"Synthetic overflow regression pilot issue "+str(number),
        "sourceContext":{"source":SOURCE,"githubRepoContext":{"startingBranch":"main"}},
        "prompt":prompt,
        "requirePlanApproval":False,
        "automationMode":"AUTO_CREATE_PR",
    }

def validate_result(result: dict, diff: dict) -> dict:
    """Validate a *mock* agent session plus independent mocked diff metadata.

    Real deployments must additionally verify GitHub API PR actor/commit/base,
    original protected QA workflows and actual CI red/green receipts.
    """
    outputs=result.get("outputs") or []
    prs=[o["pullRequest"] for o in outputs if isinstance(o,dict) and isinstance(o.get("pullRequest"),dict)]
    _need(result.get("state")=="COMPLETED","agent run incomplete")
    _need(len(prs)==1,"missing or multiple PRs")
    url=prs[0].get("url") or ""
    _need(bool(re.fullmatch(r"https://github\.com/K-JHarris/beacon-ci-public-sandbox/pull/[1-9][0-9]*",url)),
          "PR absent or wrong repository")
    files=diff.get("files") or []
    _need(isinstance(files,list) and files==[ALLOWED_PATH],"changed files missing or outside approval")
    _need(diff.get("baseShaPinned") is True,"unverified base commit")
    _need(diff.get("nonEmptyPatch") is True and isinstance(diff.get("addedLines"),int) and diff["addedLines"]>0,
          "empty or fake PR diff")
    _need(diff.get("negativeFailsOnBase") is True and diff.get("positivePassesOnCandidate") is True,
          "independent red-green regression not demonstrated")
    _need(diff.get("sourceTestsUnchanged") is True,"acceptance tests modified")
    return {"decision":"SYNTHETIC_CONTRACT_PASS_ONLY","pr_url":url,
            "unity_editor_tests":"UNVERIFIED","windows_build":"UNVERIFIED",
            "agent_invoked":False,"private_project_access":False}

if __name__=="__main__":
    print(json.dumps({"kind":"inert-jules-contract","version":1,
                      "network_access":False,"credentials_used":False,
                      "result":"STATIC_CONTRACT_ONLY"},sort_keys=True))
