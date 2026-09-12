"""Backend coverage for: seeded login + protected session enforcement.

Criterion: "A seeded student can log in and access the protected student workspace"
and "Protected routes enforce authenticated role-based sessions".
"""

import httpx

STUDENT_EMAIL = "student@demo.samanvaya.in"
PASSWORD = "AyushDemo@2026"


def test_student_login_returns_session_and_me_succeeds():
    with httpx.Client(base_url="http://localhost:8001/api", timeout=30.0) as client:
        resp = client.post("/auth/login", json={"email": STUDENT_EMAIL, "password": PASSWORD})
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["user"]["email"] == STUDENT_EMAIL
        assert body["user"]["role"] == "student"
        assert body["user"]["name"] == "Ananya Sharma"

        # session cookie should authorize /auth/me
        me = client.get("/auth/me")
        assert me.status_code == 200, me.text
        assert me.json()["role"] == "student"


def test_login_with_wrong_password_is_rejected():
    with httpx.Client(base_url="http://localhost:8001/api", timeout=30.0) as client:
        resp = client.post("/auth/login", json={"email": STUDENT_EMAIL, "password": "wrong-password"})
        assert resp.status_code == 401, resp.text


def test_me_without_session_cookie_is_unauthorized():
    with httpx.Client(base_url="http://localhost:8001/api", timeout=30.0) as client:
        resp = client.get("/auth/me")
        assert resp.status_code == 401, resp.text


def test_logout_invalidates_session():
    with httpx.Client(base_url="http://localhost:8001/api", timeout=30.0) as client:
        login = client.post("/auth/login", json={"email": STUDENT_EMAIL, "password": PASSWORD})
        assert login.status_code == 200
        logout = client.post("/auth/logout")
        assert logout.status_code == 204
        me = client.get("/auth/me")
        assert me.status_code == 401, me.text
