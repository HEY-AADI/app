"""Backend coverage for:
- "Pariksha contains the requested detailed 25-question structure"
- "Pariksha results persist after the detailed assessment"

Fetches the question bank (asserting the 20/2/2/1 type breakdown), submits an answer for
every question (all correct, using indices mirrored from routers/assessments.py
QUESTION_BANK - "correct" is never exposed via the public /assessments/questions payload)
and verifies readiness/domain scores/gaps/recommendations are computed and persisted
(visible via /assessments/latest on a fresh request).
"""

from collections import Counter

import httpx

PASSWORD = "AyushDemo@2026"
STUDENT_EMAIL = "student@demo.samanvaya.in"

CORRECT_ANSWERS = {
    "clinical-1": 1, "clinical-2": 1, "clinical-3": 2, "clinical-4": 0,
    "knowledge-1": 0, "knowledge-2": 1, "knowledge-3": 2, "knowledge-4": 1,
    "communication-1": 1, "communication-2": 1, "communication-3": 2,
    "digital-1": 1, "digital-2": 1, "digital-3": 2,
    "industry-1": 1, "industry-2": 1, "industry-3": 1, "industry-4": 1,
    "research-1": 1, "research-2": 1,
    "assertion-1": 0, "assertion-2": 3,
    "case-1": 1, "case-2": 2,
    "scenario-1": 1,
}


def test_questions_have_25_question_detailed_structure():
    with httpx.Client(base_url="http://localhost:8001/api", timeout=30.0) as client:
        login = client.post("/auth/login", json={"email": STUDENT_EMAIL, "password": PASSWORD})
        assert login.status_code == 200

        questions_resp = client.get("/assessments/questions")
        assert questions_resp.status_code == 200
        questions = questions_resp.json()
        assert len(questions) == 25
        assert set(q["id"] for q in questions) == set(CORRECT_ANSWERS)
        counts = Counter(q["question_type"] for q in questions)
        assert counts == {"mcq": 20, "assertion_reasoning": 2, "case_based": 2, "scenario_based": 1}


def test_submit_all_25_answers_persists_result():
    with httpx.Client(base_url="http://localhost:8001/api", timeout=30.0) as client:
        login = client.post("/auth/login", json={"email": STUDENT_EMAIL, "password": PASSWORD})
        assert login.status_code == 200

        questions = client.get("/assessments/questions").json()
        assert len(questions) == 25

        # Submitting fewer than all 25 answers must be rejected.
        partial = client.post("/assessments/submit", json={"answers": [{"question_id": questions[0]["id"], "option_index": 0}]})
        assert partial.status_code == 422

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
