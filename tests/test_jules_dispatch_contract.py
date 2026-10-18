import unittest
from tools.jules_dispatch_contract import ALLOWED_PATH, REPO, OWNER, Reject, make_request, validate_result

def event():
    return {"repository":{"full_name":REPO},
            "sender":{"login":OWNER}, "action":"labeled",
            "issue":{"number":17,"user":{"login":OWNER},
                     "labels":[{"name":"integration-approved"}],
                     "body":"TASK: SYNTHETIC_WILL_OVERFLOW_FIX\nACCEPTANCE: Fix overflow without disabling tests\nFORBIDDEN: Policy, test and workflow changes"}}

def result():
    return {"state":"COMPLETED","outputs":[{"pullRequest":{"url":"https://github.com/K-JHarris/beacon-ci-public-sandbox/pull/123"}}]}

def diff():
    return {"files":[ALLOWED_PATH],"baseShaPinned":True,"nonEmptyPatch":True,
            "addedLines":4,"negativeFailsOnBase":True,
            "positivePassesOnCandidate":True,"sourceTestsUnchanged":True}

class TestInertJulesContract(unittest.TestCase):
 def test_valid_spec_contract_only(self):
    x=make_request(event())
    self.assertEqual("AUTO_CREATE_PR",x["automationMode"])
    self.assertFalse(x["requirePlanApproval"])
    self.assertEqual("main",x["sourceContext"]["githubRepoContext"]["startingBranch"])
    self.assertNotIn("token",str(x).lower())
 def test_no_cross_repo_or_actor(self):
    for name,value in [("repository",{"full_name":"K-JHarris/Beacon-Lightbane"}),
                       ("sender",{"login":"random-user"}),("action","issue_comment")]:
        e=event();e[name]=value
        with self.assertRaises(Reject):make_request(e)
 def test_requires_owner_issue_author(self):
    e=event();e["issue"]["user"]["login"]="random-user"
    with self.assertRaises(Reject):make_request(e)
 def test_approval_label_and_exact_contract(self):
    for edit in ["missing_label","missing_scope","different_task","oversize"]:
        e=event()
        if edit=="missing_label": e["issue"]["labels"]=[]
        if edit=="missing_scope": e["issue"]["body"]="TASK: SYNTHETIC_WILL_OVERFLOW_FIX"
        if edit=="different_task": e["issue"]["body"]=e["issue"]["body"].replace("SYNTHETIC_WILL_OVERFLOW_FIX","REAL_PRODUCTION_CHANGE")
        if edit=="oversize": e["issue"]["body"]+="X"*5000
        with self.assertRaises(Reject):make_request(e)
 def test_realistic_pass_still_unverified_unity(self):
    r=validate_result(result(),diff())
    self.assertEqual("SYNTHETIC_CONTRACT_PASS_ONLY",r["decision"])
    self.assertEqual("UNVERIFIED",r["windows_build"])
    self.assertFalse(r["agent_invoked"])
 def test_reject_empty_or_wrong_pr(self):
    for update in [{"outputs":[]},{"state":"RUNNING"},
                   {"outputs":[{"pullRequest":{"url":"https://github.com/K-JHarris/Beacon-Lightbane/pull/2"}}]}]:
        r=result();r.update(update)
        with self.assertRaises(Reject):validate_result(r,diff())
 def test_reject_policy_or_test_edit(self):
    for paths in [[],[ALLOWED_PATH,".github/workflows/qa.yml"],
                  ["Assets/BeaconPoc/Tests/Editor/WillMathTests.cs"],[ALLOWED_PATH,ALLOWED_PATH]]:
        d=diff();d["files"]=paths
        with self.assertRaises(Reject):validate_result(result(),d)
 def test_require_independent_red_green(self):
    for name in ["baseShaPinned","nonEmptyPatch","negativeFailsOnBase","positivePassesOnCandidate","sourceTestsUnchanged"]:
        d=diff();d[name]=False
        with self.assertRaises(Reject):validate_result(result(),d)
 def test_reject_fake_no_op_diff(self):
    d=diff();d["addedLines"]=0
    with self.assertRaises(Reject):validate_result(result(),d)
