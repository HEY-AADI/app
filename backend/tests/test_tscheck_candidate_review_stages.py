"""Backend coverage for: "Blind-first candidate review hides identity and institution
initially" and "Candidate identity is revealed in the requested stages".

Uses the seeded panchakarma-clinic candidate application (documented in the briefing as
reset to "Under Review" before this test run). Verifies the blind state, then drives it
through Shortlisted (name/email revealed, institution still hidden) and Interview
(institution revealed too), confirming persistence via a fresh GET after each move.
"""

import httpx
import pytest

BASE_URL = "http://localhost:8001/api"
PASSWORD = "AyushDemo@2026"
EMPLOYER_EMAIL = "employer@demo.samanvaya.in"
OPPORTUNITY_ID = "panchakarma-clinic"


def _find_seeded_candidate(client: httpx.Client) -> dict:
    resp = client.get(f"/employer/opportunities/{OPPORTUNITY_ID}/candidates")
    assert resp.status_code == 200, resp.text
    candidates = resp.json()
    assert candidates, "expected the seeded panchakarma-clinic demo application to exist"
    return candidates[0]


def test_blind_review_then_staged_identity_reveal():
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        login = client.post("/auth/login", json={"email": EMPLOYER_EMAIL, "password": PASSWORD})
        assert login.status_code == 200, login.text

        candidate = _find_seeded_candidate(client)
        if candidate["status"] != "Under Review":
            pytest.skip(
                f"seeded panchakarma-clinic candidate already advanced to '{candidate['status']}' "
                "by a previous run of this idempotent staging test; blind-state assertions require "
                "a fresh 'Under Review' seed (see briefing seed_facts)."
            )
        app_id = candidate["application_id"]

        # Blind state: no name/email/institution, but code/readiness/skills/evidence present
        assert candidate["name"] is None
        assert candidate["email"] is None
        assert candidate["institution"] is None
        assert candidate["identity_revealed"] is False
        assert candidate["institution_revealed"] is False
        assert candidate["candidate_code"].startswith("AYU-")
        assert isinstance(candidate["readiness"], int)
        assert isinstance(candidate["evidence_count"], int)
        assert isinstance(candidate["skills"], list)

        # Move to Shortlisted -> name/email revealed, institution still hidden
        shortlist_resp = client.patch(f"/employer/applications/{app_id}", json={"status": "Shortlisted"})
        assert shortlist_resp.status_code == 200, shortlist_resp.text
        shortlisted = shortlist_resp.json()
        assert shortlisted["status"] == "Shortlisted"
        assert shortlisted["name"] is not None
        assert shortlisted["email"] is not None
        assert shortlisted["institution"] is None
        assert shortlisted["identity_revealed"] is True
        assert shortlisted["institution_revealed"] is False

        # Persists after a fresh request
        recheck = client.get(f"/employer/opportunities/{OPPORTUNITY_ID}/candidates")
        recheck_candidate = next(c for c in recheck.json() if c["application_id"] == app_id)
        assert recheck_candidate["status"] == "Shortlisted"
        assert recheck_candidate["institution"] is None

        # Move to Interview -> institution now revealed too
        interview_resp = client.patch(f"/employer/applications/{app_id}", json={"status": "Interview"})
        assert interview_resp.status_code == 200, interview_resp.text
        interviewed = interview_resp.json()
        assert interviewed["status"] == "Interview"
        assert interviewed["name"] is not None
        assert interviewed["institution"] is not None
        assert interviewed["institution_revealed"] is True

        recheck_2 = client.get(f"/employer/opportunities/{OPPORTUNITY_ID}/candidates")
        recheck_2_candidate = next(c for c in recheck_2.json() if c["application_id"] == app_id)
        assert recheck_2_candidate["status"] == "Interview"
        assert recheck_2_candidate["institution"] is not None


def test_non_employer_cannot_view_or_stage_candidates():
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        login = client.post("/auth/login", json={"email": "student@demo.samanvaya.in", "password": PASSWORD})
        assert login.status_code == 200
        resp = client.get(f"/employer/opportunities/{OPPORTUNITY_ID}/candidates")
        assert resp.status_code == 403, resp.text
