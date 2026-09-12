"""Backend coverage for: "Persistent opportunities and applications work end to end".

Applies as the seeded student to a seeded opportunity (idempotent — safe to rerun),
confirms it is listed under /applications/me, and confirms a non-student role is
rejected from applying.
"""

import httpx

PASSWORD = "AyushDemo@2026"
STUDENT_EMAIL = "student@demo.samanvaya.in"
EMPLOYER_EMAIL = "employer@demo.samanvaya.in"
OPPORTUNITY_ID = "panchakarma-clinic"


def test_student_can_apply_and_application_persists():
    with httpx.Client(base_url="http://localhost:8001/api", timeout=30.0) as client:
        login = client.post("/auth/login", json={"email": STUDENT_EMAIL, "password": PASSWORD})
        assert login.status_code == 200

        opportunities = client.get("/opportunities")
        assert opportunities.status_code == 200
        ids = [item["id"] for item in opportunities.json()]
        assert OPPORTUNITY_ID in ids

        apply_resp = client.post(f"/opportunities/{OPPORTUNITY_ID}/apply")
        assert apply_resp.status_code in (200, 201), apply_resp.text
        application = apply_resp.json()
        assert application["opportunity_id"] == OPPORTUNITY_ID

        # idempotent re-apply returns the same saved application
        reapply = client.post(f"/opportunities/{OPPORTUNITY_ID}/apply")
        assert reapply.status_code in (200, 201)
        assert reapply.json()["id"] == application["id"]

        mine = client.get("/applications/me")
        assert mine.status_code == 200
        app_ids = [item["id"] for item in mine.json()]
        assert application["id"] in app_ids

        internships = client.get("/internships/me")
        assert internships.status_code == 200
        titles = [item["opportunity_title"] for item in internships.json()]
        assert application["opportunity_title"] in titles


def test_non_student_role_cannot_apply():
    with httpx.Client(base_url="http://localhost:8001/api", timeout=30.0) as client:
        login = client.post("/auth/login", json={"email": EMPLOYER_EMAIL, "password": PASSWORD})
        assert login.status_code == 200
        apply_resp = client.post(f"/opportunities/{OPPORTUNITY_ID}/apply")
        assert apply_resp.status_code == 403, apply_resp.text
