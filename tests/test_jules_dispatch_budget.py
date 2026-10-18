import unittest
from tools.jules_dispatch_contract import LABEL, Reject, authorize_dispatch
from test_jules_dispatch_contract import event

def controls():
    return dict(ownerAuthorized=True, freeAccountVerified=True,
                paidFallbackEnabled=False, remainingTasks=1, maxCreates=1,
                priorAttemptState="NEVER_ATTEMPTED", journalVerified=True)

class TestBudgetAndRecovery(unittest.TestCase):
    def request(self):
        e=event(); e["label"]={"name":LABEL}; return e
    def test_valid_is_still_inert(self):
        out=authorize_dispatch(self.request(),controls())
        self.assertEqual(out["reservation"],"NOT_CREATED")
        self.assertFalse(out["network_access"])
    def test_missing_each_control(self):
        for key in controls():
            with self.subTest(key=key):
                c=controls(); del c[key]
                with self.assertRaises(Reject): authorize_dispatch(self.request(),c)
    def test_quota_and_budgets(self):
        for key, values in [("remainingTasks",[0,-1,True,"15",None]),
                            ("maxCreates",[0,2,True,"1"])]:
            for value in values:
                with self.subTest(key=key,value=value):
                    c=controls(); c[key]=value
                    with self.assertRaises(Reject): authorize_dispatch(self.request(),c)
    def test_never_blindly_repost(self):
        for state in ["RESERVED","POST_OUTCOME_UNKNOWN","SESSION_CREATED","COMPLETED","FAILED",None]:
            c=controls(); c["priorAttemptState"]=state
            with self.subTest(state=state), self.assertRaises(Reject):
                authorize_dispatch(self.request(),c)
    def test_no_other_label_retrigger(self):
        e=self.request(); e["label"]={"name":"documentation"}
        with self.assertRaises(Reject): authorize_dispatch(e,controls())
    def test_no_pr_or_boolean_issue(self):
        for key,value in [("pull_request",{"url":"synthetic"}),("number",True)]:
            e=self.request(); e["issue"][key]=value
            with self.assertRaises(Reject): authorize_dispatch(e,controls())
    def test_consent_and_free_tier_fail_closed(self):
        for key,value in [("ownerAuthorized",False),("freeAccountVerified",False),
                          ("paidFallbackEnabled",True),("journalVerified",False)]:
            c=controls(); c[key]=value
            with self.subTest(key=key), self.assertRaises(Reject):
                authorize_dispatch(self.request(),c)
    def test_invalid_schema(self):
        for e,c in [(None,controls()),(self.request(),None)]:
            with self.assertRaises(Reject): authorize_dispatch(e,c)
