"""Backend coverage for: "Student profile editing persists provenance-backed data".

Patches the seeded student's profile with new education, AYUSH system, graduation year,
interests, a provenance-backed skill and a portfolio evidence item, then re-fetches the
profile on a fresh request to confirm the values persisted in PostgreSQL.
"""

import httpx

PASSWORD = "AyushDemo@2026"
STUDENT_EMAIL = "student@demo.samanvaya.in"


def test_profile_patch_persists_provenance_backed_data():
    with httpx.Client(base_url="http://localhost:8001/api", timeout=30.0) as client:
        login = client.post("/auth/login", json={"email": STUDENT_EMAIL, "password": PASSWORD})
        assert login.status_code == 200

        before = client.get("/profile/me")
        assert before.status_code == 200
        original = before.json()

        payload = {
            "education": "tscheck-profile-update BAMS final year",
            "ayush_system": "Siddha",
            "graduation_year": 2027,
            "interests": ["tscheck-quality-assurance", "tscheck-research"],
            "skills": [
                {"name": "tscheck-GMP fundamentals", "level": 72, "provenance": "Employer verified", "evidence": "tscheck-QA audit log"},
            ],
            "portfolio_evidence": [
                {"title": "tscheck-QA workflow sample", "issuer": "Arogya Botanicals", "evidence_type": "Internship", "date": "2026-03-01"},
            ],
        }
        patch_resp = client.patch("/profile/me", json=payload)
        assert patch_resp.status_code == 200, patch_resp.text
        updated = patch_resp.json()
        assert updated["education"] == payload["education"]
        assert updated["ayush_system"] == "Siddha"
        assert updated["graduation_year"] == 2027

        # Re-fetch on a fresh request to prove PostgreSQL persistence, not just an echo.
        after = client.get("/profile/me")
        assert after.status_code == 200
        persisted = after.json()
        assert persisted["education"] == payload["education"]
        assert persisted["ayush_system"] == "Siddha"
        assert persisted["graduation_year"] == 2027
        assert persisted["interests"] == payload["interests"]
        assert persisted["skills"][0]["name"] == "tscheck-GMP fundamentals"
        assert persisted["skills"][0]["provenance"] == "Employer verified"
        assert persisted["skills"][0]["evidence"] == "tscheck-QA audit log"
        assert persisted["portfolio_evidence"][0]["title"] == "tscheck-QA workflow sample"

        # Restore the seeded profile so the fixture doesn't leak into other checks.
        restore = client.patch("/profile/me", json={
            "education": original["education"], "ayush_system": original["ayush_system"],
            "graduation_year": original["graduation_year"], "interests": original["interests"],
            "skills": original["skills"], "portfolio_evidence": original["portfolio_evidence"],
        })
        assert restore.status_code == 200


def test_profile_requires_student_role():
    with httpx.Client(base_url="http://localhost:8001/api", timeout=30.0) as client:
        login = client.post("/auth/login", json={"email": "employer@demo.samanvaya.in", "password": PASSWORD})
        assert login.status_code == 200
        resp = client.get("/profile/me")
        assert resp.status_code == 403
