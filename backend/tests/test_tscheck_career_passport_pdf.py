"""Backend coverage for: "Career Passport downloads as a professional PDF".

Downloads GET /api/profile/passport as the seeded student, confirms the filename/media
type contract, a valid %PDF header, and (by decoding the reportlab ASCII85+Flate content
stream with stdlib only) that the rendered text includes the student's identity, the
skills/provenance section, internship experience and the prototype disclaimer.
"""

import base64
import zlib

import httpx

BASE_URL = "http://localhost:8001/api"
PASSWORD = "AyushDemo@2026"
STUDENT_EMAIL = "student@demo.samanvaya.in"


def _decode_reportlab_text_stream(pdf_bytes: bytes) -> bytes:
    """Best-effort stdlib decode of the single ASCII85+Flate content stream reportlab emits."""
    start = pdf_bytes.index(b"stream") + len(b"stream")
    while pdf_bytes[start] in (13, 10):
        start += 1
    end = pdf_bytes.index(b"endstream", start)
    chunk = pdf_bytes[start:end].rstrip(b"\r\n")
    raw = base64.a85decode(chunk, adobe=True)
    return zlib.decompress(raw)


def test_career_passport_pdf_download_contains_expected_sections():
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        login = client.post("/auth/login", json={"email": STUDENT_EMAIL, "password": PASSWORD})
        assert login.status_code == 200, login.text

        profile = client.get("/profile/me")
        assert profile.status_code == 200
        student_name = profile.json()["name"]

        passport_resp = client.get("/profile/passport")
        assert passport_resp.status_code == 200, passport_resp.text
        document = passport_resp.json()
        assert document["filename"] == "samanvaya-career-passport.pdf"
        assert document["media_type"] == "application/pdf"

        pdf_bytes = base64.b64decode(document["content_base64"])
        assert pdf_bytes[:5] == b"%PDF-"

        text = _decode_reportlab_text_stream(pdf_bytes)
        assert student_name.encode() in text
        assert b"CAREER PASSPORT" in text
        assert b"VERIFIED SKILLS" in text
        assert b"EXPERIENCE" in text
        assert b"prototype" in text.lower()
        assert b"not an official government credential" in text.lower()


def test_non_student_cannot_download_passport():
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        login = client.post("/auth/login", json={"email": "employer@demo.samanvaya.in", "password": PASSWORD})
        assert login.status_code == 200
        resp = client.get("/profile/passport")
        assert resp.status_code == 403, resp.text
