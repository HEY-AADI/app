"""Backend coverage for: "Pariksha adaptive assessment works and persists results".

Fetches the question bank, submits all-correct answers for the seeded student and
verifies readiness/domain scores/gaps/recommendations are computed and persisted
(visible via /assessments/latest on a fresh request).
"""

import httpx

PASSWORD = "AyushDemo@2026"
STUDENT_EMAIL = "student@demo.samanvaya.in"

# Correct-option indices mirror routers/assessments.py QUESTION_BANK (not exposed via the
# public /assessments/questions payload, which omits "correct").
CORRECT_ANSWERS = {
    "clinical-1": 1, "clinical-2": 1, "knowledge-1": 0, "knowledge-2": 1,
    "communication-1": 1, "communication-2": 1, "digital-1": 1, "digital-2": 1,
    "industry-1": 1, "industry-2": 1, "industry-3": 1, "research-1": 1,
}


def test_submit_assessment_persists_result():
    with httpx.Client(base_url="http://localhost:8001/api", timeout=30.0) as client:
        login = client.post("/auth/login", json={"email": STUDENT_EMAIL, "password": PASSWORD})
        assert login.status_code == 200

        questions_resp = client.get("/assessments/questions")
        assert questions_resp.status_code == 200
        questions = questions_resp.json()
        assert len(questions) == 12
        assert set(q["id"] for q in questions) == set(CORRECT_ANSWERS)

        answers = [{"question_id": q["id"], "option_index": CORRECT_ANSWERS[q["id"]]} for q in questions]
        submit_resp = client.post("/assessments/submit", json={"answers": answers})
        assert submit_resp.status_code == 200, submit_resp.text
        result = submit_resp.json()
        assert result["readiness"] == 100
        assert result["skill_scores"]
        assert result["gaps"] == []
        assert result["recommendations"] == []

        latest_resp = client.get("/assessments/latest")
        assert latest_resp.status_code == 200
        latest = latest_resp.json()
        assert latest is not None
        assert latest["id"] == result["id"]
        assert latest["readiness"] == 100
