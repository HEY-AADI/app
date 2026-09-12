"""Backend coverage for:
- "Karma supports two-sided check-ins and divergence alerts"
- "The internship evidence pack is downloadable"

Finds the seeded student's active Week 4 internship, confirms the seeded mentor
response is already present, submits a conflicting student Week 4 response and
confirms both sides persist with a divergence alert, then fetches the evidence pack.
"""

import httpx

PASSWORD = "AyushDemo@2026"
STUDENT_EMAIL = "student@demo.samanvaya.in"


def _login(client: httpx.Client) -> None:
    login = client.post("/auth/login", json={"email": STUDENT_EMAIL, "password": PASSWORD})
    assert login.status_code == 200


def test_student_checkin_persists_alongside_mentor_and_flags_divergence():
    with httpx.Client(base_url="http://localhost:8001/api", timeout=30.0) as client:
        _login(client)
        internships = client.get("/internships/me")
        assert internships.status_code == 200
        active = next((item for item in internships.json() if item["week"] >= 4), None)
        assert active is not None, "seeded Week 4 internship not found for demo student"
        internship_id = active["id"]

        before = client.get(f"/internships/{internship_id}/check-ins", params={"week": 4})
        assert before.status_code == 200
        before_data = before.json()
        assert before_data["mentor"] is not None
        assert before_data["mentor"]["meeting_frequency"] == "Weekly"
        assert before_data["mentor"]["useful_feedback"] == "Yes"

        # Submit a conflicting student response (mentor says Weekly/Yes -> student says Never/No).
        submit = client.post(
            f"/internships/{internship_id}/check-ins",
            json={"week": 4, "meeting_frequency": "Never", "useful_feedback": "No", "reflection": "tscheck-karma: no weekly meeting occurred this cycle."},
        )
        assert submit.status_code == 200, submit.text
        summary = submit.json()
        assert summary["student"]["meeting_frequency"] == "Never"
        assert summary["student"]["reflection"] == "tscheck-karma: no weekly meeting occurred this cycle."
        assert summary["mentor"]["meeting_frequency"] == "Weekly"
        assert summary["divergence_alert"] is True

        # Re-fetch on a fresh request to confirm both sides persisted separately.
        after = client.get(f"/internships/{internship_id}/check-ins", params={"week": 4})
        assert after.status_code == 200
        after_data = after.json()
        assert after_data["student"]["meeting_frequency"] == "Never"
        assert after_data["mentor"]["meeting_frequency"] == "Weekly"
        assert after_data["divergence_alert"] is True


def test_evidence_pack_download_contains_both_sides():
    with httpx.Client(base_url="http://localhost:8001/api", timeout=30.0) as client:
        _login(client)
        internships = client.get("/internships/me")
        active = next((item for item in internships.json() if item["week"] >= 4), None)
        assert active is not None
        internship_id = active["id"]

        pack = client.get(f"/internships/{internship_id}/evidence-pack")
        assert pack.status_code == 200, pack.text
        data = pack.json()
        assert data["internship_id"] == internship_id
        assert data["opportunity_title"] == active["opportunity_title"]
        assert data["deliverable"]
        assert data["mentor_assessment"]
        assert data["student_reflection"]
        assert "Week 4" in data["completion_status"]


def test_checkins_reject_other_role():
    with httpx.Client(base_url="http://localhost:8001/api", timeout=30.0) as client:
        login = client.post("/auth/login", json={"email": "employer@demo.samanvaya.in", "password": PASSWORD})
        assert login.status_code == 200
        student_login = httpx.Client(base_url="http://localhost:8001/api", timeout=30.0)
        student_login.post("/auth/login", json={"email": STUDENT_EMAIL, "password": PASSWORD})
        internships = student_login.get("/internships/me").json()
        active = next((item for item in internships if item["week"] >= 4), None)
        assert active is not None
        resp = client.get(f"/internships/{active['id']}/check-ins", params={"week": 4})
        assert resp.status_code == 403
        student_login.close()
