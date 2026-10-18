"""Secret-free mocked safety checks. NEVER contact Jules or create GitHub refs."""
import os
import unittest
from unittest.mock import patch
from tools import jules_onecreate_pilot as pilot

ENV = {
    "GITHUB_REPOSITORY": pilot.REPO, "GITHUB_ACTOR": "K-JHarris",
    "GITHUB_REF": "refs/heads/main", "GITHUB_EVENT_NAME": "workflow_dispatch",
    "GITHUB_RUN_ATTEMPT": "1", "PILOT_CONFIRM": pilot.CONFIRM,
    "GH_TOKEN": "test-gh-placeholder", "JULES_API_KEY": "test-jules-placeholder",
}


class PilotGuardTests(unittest.TestCase):
    def test_incorrect_gate_stops_before_network(self):
        for field, value in [
            ("GITHUB_REPOSITORY", "other/repo"),
            ("GITHUB_ACTOR", "other"),
            ("GITHUB_REF", "refs/heads/pilot"),
            ("GITHUB_EVENT_NAME", "push"),
            ("GITHUB_RUN_ATTEMPT", "2"),
            ("PILOT_CONFIRM", "no"),
        ]:
            with self.subTest(field=field), patch.dict(os.environ, {**ENV, field: value}, clear=True):
                with patch.object(pilot, "request", side_effect=AssertionError("network contacted")):
                    with self.assertRaisesRegex(RuntimeError, "Unapproved"):
                        pilot.main()

    def test_no_secret_stops_before_network(self):
        with patch.dict(os.environ, {**ENV, "JULES_API_KEY": ""}, clear=True):
            with patch.object(pilot, "request", side_effect=AssertionError("network contacted")):
                with self.assertRaisesRegex(RuntimeError, "missing"):
                    pilot.main()

    def test_wrong_pin_stops_before_reservation(self):
        with patch.dict(os.environ, ENV, clear=True):
            with patch.object(pilot, "request", return_value={"object": {"sha": "changed"}}):
                with self.assertRaisesRegex(RuntimeError, "base changed"):
                    pilot.main()

    def test_exactly_one_post_after_reservation(self):
        calls = []

        def responder(method, url, **kw):
            calls.append((method, url, kw.get("body")))
            if "/git/ref/heads/" in url:
                return {"object": {"sha": pilot.PILOT_BASE}}
            if "/sources?" in url:
                return {"sources": [{
                    "name": "sources/github/K-JHarris/beacon-ci-public-sandbox",
                    "githubRepo": {"owner": "K-JHarris", "repo": "beacon-ci-public-sandbox"},
                }]}
            if url.endswith("/git/refs"):
                return {"ref": pilot.RESERVATION_REF}
            if url.endswith("/sessions"):
                return {"name": "sessions/123456"}
            raise AssertionError("unexpected network")

        with patch.dict(os.environ, ENV, clear=True):
            with patch.object(pilot, "request", side_effect=responder):
                pilot.main()
        posts = [url for method, url, _ in calls if method == "POST"]
        self.assertEqual(posts, [pilot.API_GH + "/git/refs", pilot.API_JULES + "/sessions"])
        self.assertTrue(calls[-1][2]["requirePlanApproval"])
        self.assertNotIn("test-jules-placeholder", str(calls[-1][2]))

    def test_reservation_failure_blocks_api_create(self):
        from urllib.error import HTTPError
        posts = []

        def responder(method, url, **kw):
            if "/git/ref/heads/" in url:
                return {"object": {"sha": pilot.PILOT_BASE}}
            if "/sources?" in url:
                return {"sources": [{
                    "name": "sources/github/K-JHarris/beacon-ci-public-sandbox",
                    "githubRepo": {"owner": "K-JHarris", "repo": "beacon-ci-public-sandbox"},
                }]}
            if method == "POST":
                posts.append(url)
                raise HTTPError(url, 422, "already reserved", {}, None)
            raise AssertionError("unexpected network")

        with patch.dict(os.environ, ENV, clear=True):
            with patch.object(pilot, "request", side_effect=responder):
                with self.assertRaisesRegex(RuntimeError, "reservation failed"):
                    pilot.main()
        self.assertEqual(posts, [pilot.API_GH + "/git/refs"])

    def test_only_exact_sandbox_source_is_accepted(self):
        wrong = [{"name": "sources/github/K-JHarris/Beacon-Lightbane",
                  "githubRepo": {"owner": "K-JHarris", "repo": "Beacon-Lightbane"}}]
        with patch.object(pilot, "request", return_value={"sources": wrong}):
            with self.assertRaisesRegex(RuntimeError, "absent"):
                pilot.only_source({})
