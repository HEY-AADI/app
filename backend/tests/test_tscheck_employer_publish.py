"""Backend coverage for: "Employer can create a complete opportunity draft and publish it
only after policy validation" and "Published employer opportunities become available
through the public opportunity API".

Creates a uniquely-titled Internship draft, verifies publish is rejected (422) while
required fields are missing, and verifies the draft is invisible from public discovery
until a fully-valid publish succeeds and it becomes visible at GET /api/opportunities/{id}.
"""

import time
import uuid

import httpx

BASE_URL = "http://localhost:8001/api"
PASSWORD = "AyushDemo@2026"
EMPLOYER_EMAIL = "employer@demo.samanvaya.in"


def _draft_payload(title: str, *, mentor: str = "", deliverable: str = "", stipend: str = "") -> dict:
    return {
        "type": "Internship",
        "title": title,
        "system": "Ayurveda",
        "skills": ["Panchakarma", "Documentation"],
        "eligibility": "BAMS or relevant AYUSH qualification",
        "stipend": stipend,
        "location": "Pune, Maharashtra",
        "mode": "Hybrid",
        "duration": "8 weeks",
        "mentor": mentor,
        "deliverable": deliverable,
        "accessibility": "Accessible workplace details available on request",
        "deadline": "30 days from publication",
    }


def test_publish_rejected_without_mentor_deliverable_stipend_then_succeeds_and_appears_public():
    unique = f"tscheck-employer-publish-{uuid.uuid4().hex[:8]}"
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        login = client.post("/auth/login", json={"email": EMPLOYER_EMAIL, "password": PASSWORD})
        assert login.status_code == 200, login.text

        # 1. Create an incomplete draft (blank mentor/deliverable/stipend for an Internship)
        incomplete_title = f"{unique}-incomplete"
        create_resp = client.post("/employer/opportunities", json=_draft_payload(incomplete_title))
        assert create_resp.status_code == 422, create_resp.text  # pydantic min_length rejects empty fields at creation

        # Create a *saveable* draft (passes pydantic min-length) but still policy-invalid to publish:
        # deliverable long enough to satisfy the model but mentor left effectively blank via whitespace.
        weak_payload = _draft_payload(
            incomplete_title,
            mentor="  ",
            deliverable="A sufficiently long deliverable description for validation.",
            stipend="₹8,000 / month",
        )
        weak_create = client.post("/employer/opportunities", json=weak_payload)
        assert weak_create.status_code == 201, weak_create.text
        weak_draft = weak_create.json()
        assert weak_draft["publication_status"] == "draft"

        weak_publish = client.post(f"/employer/opportunities/{weak_draft['id']}/publish")
        assert weak_publish.status_code == 422, weak_publish.text
        assert "mentor" in weak_publish.text.lower()

        # Draft must remain absent from public discovery while unpublished
        public_get_before = client.get(f"/opportunities/{weak_draft['id']}")
        assert public_get_before.status_code == 404, public_get_before.text
        public_list_before = client.get("/opportunities")
        assert weak_draft["id"] not in [item["id"] for item in public_list_before.json()]

        # 2. Create a fully-valid draft and publish it
        valid_title = f"{unique}-valid"
        valid_payload = _draft_payload(
            valid_title,
            mentor="Dr. Asha Verma, Clinical Lead",
            deliverable="Deliver a documented quality-audit report for the panchakarma unit.",
            stipend="₹9,500 / month",
        )
        valid_create = client.post("/employer/opportunities", json=valid_payload)
        assert valid_create.status_code == 201, valid_create.text
        valid_draft = valid_create.json()
        assert valid_draft["publication_status"] == "draft"

        # Still absent from public discovery pre-publish
        pre_publish_public = client.get(f"/opportunities/{valid_draft['id']}")
        assert pre_publish_public.status_code == 404

        publish_resp = client.post(f"/employer/opportunities/{valid_draft['id']}/publish")
        assert publish_resp.status_code == 200, publish_resp.text
        published = publish_resp.json()
        assert published["publication_status"] == "published"

        # 3. Published opportunity is now available through the public API
        public_get_after = client.get(f"/opportunities/{valid_draft['id']}")
        assert public_get_after.status_code == 200, public_get_after.text
        assert public_get_after.json()["title"] == valid_title

        public_list_after = client.get("/opportunities")
        assert valid_draft["id"] in [item["id"] for item in public_list_after.json()]


def test_non_employer_cannot_create_or_publish_drafts():
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        login = client.post("/auth/login", json={"email": "student@demo.samanvaya.in", "password": PASSWORD})
        assert login.status_code == 200
        resp = client.post("/employer/opportunities", json=_draft_payload(f"tscheck-employer-publish-forbidden-{uuid.uuid4().hex[:6]}", mentor="Mx", deliverable="A sufficiently long deliverable text.", stipend="₹1"))
        assert resp.status_code == 403, resp.text
