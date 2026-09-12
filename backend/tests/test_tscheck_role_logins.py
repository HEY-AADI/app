"""Backend coverage for: "Each supported role has a working seeded login".

Verifies employer, alumni/mentor, institution and ministry seeded accounts can log in
and that /auth/me reports the matching role.
"""

import httpx

PASSWORD = "AyushDemo@2026"
ROLE_EMAILS = {
    "employer": "employer@demo.samanvaya.in",
    "alumni": "alumni@demo.samanvaya.in",
    "institution": "institution@demo.samanvaya.in",
    "ministry": "ministry@demo.samanvaya.in",
}


def test_each_seeded_role_logs_in_and_reports_matching_role():
    for role, email in ROLE_EMAILS.items():
        with httpx.Client(base_url="http://localhost:8001/api", timeout=30.0) as client:
            login = client.post("/auth/login", json={"email": email, "password": PASSWORD})
            assert login.status_code == 200, f"{role} login failed: {login.text}"
            body = login.json()
            assert body["user"]["role"] == role, f"{role} login returned role {body['user']['role']}"
            assert body["user"]["email"] == email

            me = client.get("/auth/me")
            assert me.status_code == 200, me.text
            assert me.json()["role"] == role
