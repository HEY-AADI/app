from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from lib.db import get_pool
from models.assessment import AssessmentQuestion, AssessmentResult, AssessmentStartResponse, AssessmentSubmit
from routers.auth import get_current_user

router = APIRouter(prefix="/assessments", tags=["assessments"])

QUESTION_BANK = [
    {"id": "clinical-1", "prompt": "Which action best supports safe Panchakarma preparation?", "domain": "Clinical skills", "skill": "Panchakarma", "options": ["Skip patient history", "Confirm assessment and contraindications", "Use one protocol for everyone", "Avoid documenting observations"], "correct": 1, "difficulty": 1, "question_type": "mcq"},
    {"id": "clinical-2", "prompt": "A patient reports discomfort during a supervised procedure. What is the best first response?", "domain": "Clinical skills", "skill": "Patient communication", "options": ["Continue silently", "Pause, listen and escalate appropriately", "Ask them to tolerate it", "End the record"], "correct": 1, "difficulty": 2, "question_type": "mcq"},
    {"id": "clinical-3", "prompt": "Which practice most directly reduces cross-contamination between supervised procedures?", "domain": "Clinical skills", "skill": "Infection prevention", "options": ["Reuse unlabelled materials", "Document only at day-end", "Follow hand hygiene and equipment-cleaning protocols", "Keep treatment areas dim"], "correct": 2, "difficulty": 1, "question_type": "mcq"},
    {"id": "clinical-4", "prompt": "Before recording a patient image for a learning portfolio, you should first:", "domain": "Clinical skills", "skill": "Consent", "options": ["Obtain informed, documented consent", "Remove only the patient's name", "Ask after uploading it", "Assume teaching use is permitted"], "correct": 0, "difficulty": 2, "question_type": "mcq"},
    {"id": "knowledge-1", "prompt": "What is the purpose of a standard operating procedure?", "domain": "AYUSH knowledge", "skill": "Process knowledge", "options": ["Create repeatable, documented practice", "Replace all judgement", "Reduce supervision", "Hide variation"], "correct": 0, "difficulty": 1, "question_type": "mcq"},
    {"id": "knowledge-2", "prompt": "Which statement best describes evidence-informed AYUSH practice?", "domain": "AYUSH knowledge", "skill": "Evidence literacy", "options": ["Only tradition matters", "Use relevant evidence with clinical context", "Avoid recording outcomes", "Copy every published protocol"], "correct": 1, "difficulty": 2, "question_type": "mcq"},
    {"id": "knowledge-3", "prompt": "When a traditional formulation and a patient's current medicines may interact, the safest next step is to:", "domain": "AYUSH knowledge", "skill": "Safe practice", "options": ["Ignore current medicines", "Increase the traditional dose", "Review evidence and escalate to the qualified supervisor", "Ask the patient to decide alone"], "correct": 2, "difficulty": 2, "question_type": "mcq"},
    {"id": "knowledge-4", "prompt": "A clinical observation becomes useful evidence when it is:", "domain": "AYUSH knowledge", "skill": "Clinical evidence", "options": ["Memorable", "Structured, dated and attributable", "Shared verbally", "Written without context"], "correct": 1, "difficulty": 1, "question_type": "mcq"},
    {"id": "communication-1", "prompt": "A clear clinical handover should include:", "domain": "Communication", "skill": "Team collaboration", "options": ["Only a conclusion", "Relevant context, action and risk", "Personal opinion only", "No written follow-up"], "correct": 1, "difficulty": 1, "question_type": "mcq"},
    {"id": "communication-2", "prompt": "How should you respond when a mentor gives unclear feedback?", "domain": "Communication", "skill": "Feedback literacy", "options": ["Ignore it", "Ask for a concrete example and next step", "Defend every decision", "Wait until completion"], "correct": 1, "difficulty": 2, "question_type": "mcq"},
    {"id": "communication-3", "prompt": "Which response best checks a patient's understanding?", "domain": "Communication", "skill": "Patient education", "options": ["Ask whether they agree", "Repeat the same words more loudly", "Use teach-back in respectful language", "Give a leaflet without discussion"], "correct": 2, "difficulty": 2, "question_type": "mcq"},
    {"id": "digital-1", "prompt": "Which practice improves the quality of a digital clinical record?", "domain": "Digital skills", "skill": "Documentation", "options": ["Use shared passwords", "Record timely, structured observations", "Copy forward everything", "Delete inconvenient notes"], "correct": 1, "difficulty": 1, "question_type": "mcq"},
    {"id": "digital-2", "prompt": "A spreadsheet shows an unexpected outlier. What should you do first?", "domain": "Digital skills", "skill": "Data literacy", "options": ["Delete the row", "Check the source and definition", "Average it away", "Publish immediately"], "correct": 1, "difficulty": 2, "question_type": "mcq"},
    {"id": "digital-3", "prompt": "What is the safest way to share a student case file with an authorised reviewer?", "domain": "Digital skills", "skill": "Data privacy", "options": ["Personal messaging app", "Public drive link", "Access-controlled approved storage", "Unencrypted email attachment"], "correct": 2, "difficulty": 2, "question_type": "mcq"},
    {"id": "industry-1", "prompt": "What does GMP primarily help an organisation control?", "domain": "Industry readiness", "skill": "GMP fundamentals", "options": ["Brand colour", "Consistent quality and process control", "Recruitment only", "Social media reach"], "correct": 1, "difficulty": 1, "question_type": "mcq"},
    {"id": "industry-2", "prompt": "Which is strongest evidence of quality documentation skill?", "domain": "Industry readiness", "skill": "Quality documentation", "options": ["A self-rating", "A reviewed workflow with traceable sources", "A job title alone", "An unlabelled screenshot"], "correct": 1, "difficulty": 2, "question_type": "mcq"},
    {"id": "industry-3", "prompt": "A production process changes. What should happen to its SOP?", "domain": "Industry readiness", "skill": "Quality assurance", "options": ["Nothing", "Review, version and retrain as needed", "Delete old evidence", "Wait for an audit"], "correct": 1, "difficulty": 3, "question_type": "mcq"},
    {"id": "industry-4", "prompt": "A corrective and preventive action should begin with:", "domain": "Industry readiness", "skill": "CAPA", "options": ["Assigning blame", "Understanding and documenting the root cause", "Changing every process", "Closing the issue immediately"], "correct": 1, "difficulty": 3, "question_type": "mcq"},
    {"id": "research-1", "prompt": "A useful research question is:", "domain": "Research", "skill": "Research methods", "options": ["Broad and impossible to measure", "Specific, answerable and relevant", "Based only on assumptions", "Changed after every result"], "correct": 1, "difficulty": 1, "question_type": "mcq"},
    {"id": "research-2", "prompt": "Which action best reduces selection bias in a student survey?", "domain": "Research", "skill": "Study design", "options": ["Invite only high performers", "Define a relevant sampling approach before collection", "Remove unexpected answers", "Change criteria after analysis"], "correct": 1, "difficulty": 2, "question_type": "mcq"},
    {"id": "assertion-1", "prompt": "Choose the correct relationship between the assertion and reason.", "context": "Assertion: Version control is essential for quality documentation. Reason: It helps teams identify the approved procedure and trace changes.", "domain": "Industry readiness", "skill": "Quality documentation", "options": ["Both are true, and the reason explains the assertion", "Both are true, but the reason does not explain the assertion", "The assertion is true, but the reason is false", "The assertion is false, but the reason is true"], "correct": 0, "difficulty": 3, "question_type": "assertion_reasoning"},
    {"id": "assertion-2", "prompt": "Choose the correct relationship between the assertion and reason.", "context": "Assertion: Self-declared skill evidence should always outweigh employer-verified evidence. Reason: All evidence sources have equal confidence.", "domain": "Career readiness", "skill": "Evidence provenance", "options": ["Both are true, and the reason explains the assertion", "Both are true, but the reason does not explain the assertion", "The assertion is true, but the reason is false", "Both assertion and reason are false"], "correct": 3, "difficulty": 3, "question_type": "assertion_reasoning"},
    {"id": "case-1", "prompt": "What should the intern do first?", "context": "During a quality internship, an intern notices that the batch record and the current SOP contain different temperatures for the same step.", "domain": "Industry readiness", "skill": "Deviation handling", "options": ["Choose the lower value", "Pause the step and escalate the documented discrepancy", "Edit the batch record", "Continue and mention it later"], "correct": 1, "difficulty": 3, "question_type": "case_based"},
    {"id": "case-2", "prompt": "Which response best protects the student and the quality of the internship?", "context": "A student reports no mentor meeting for two weeks, while the mentor records weekly meetings as completed.", "domain": "Communication", "skill": "Internship check-ins", "options": ["Delete the student's response", "Automatically fail the student", "Flag the divergence and request evidence-based review", "Publish both responses publicly"], "correct": 2, "difficulty": 3, "question_type": "case_based"},
    {"id": "scenario-1", "prompt": "Which plan creates the strongest next step?", "context": "You match 7 of 9 skills for a quality internship. The missing skills are GMP fundamentals and quality documentation, and you have six hours this week.", "domain": "Career readiness", "skill": "Action planning", "options": ["Apply without reviewing the gaps", "Complete a verified introductory GMP module and create one reviewed documentation sample", "Add both skills as employer verified", "Wait until graduation"], "correct": 1, "difficulty": 3, "question_type": "scenario_based"},
]


def _public_questions() -> list[AssessmentQuestion]:
    return [AssessmentQuestion(**{key: question.get(key) for key in AssessmentQuestion.model_fields}) for question in QUESTION_BANK]


@router.get("/questions", response_model=list[AssessmentQuestion])
async def get_questions(user: dict = Depends(get_current_user)):
    return _public_questions()


@router.get("/start", response_model=AssessmentStartResponse)
async def start_assessment(user: dict = Depends(get_current_user)):
    return AssessmentStartResponse(session_id=str(uuid4()), questions=_public_questions())


@router.get("/latest", response_model=AssessmentResult | None)
async def get_latest(user: dict = Depends(get_current_user)):
    row = await get_pool().fetchrow(
        "SELECT id,readiness,skill_scores,gaps,recommendations,completed_at FROM assessment_results WHERE user_id=$1 ORDER BY completed_at DESC LIMIT 1",
        user["id"],
    )
    return AssessmentResult(**dict(row)) if row else None


@router.post("/submit", response_model=AssessmentResult)
async def submit_assessment(payload: AssessmentSubmit, user: dict = Depends(get_current_user)):
    answer_map = {answer.question_id: answer.option_index for answer in payload.answers}
    expected_ids = {question["id"] for question in QUESTION_BANK}
    if len(payload.answers) != len(QUESTION_BANK) or set(answer_map) != expected_ids:
        raise HTTPException(status_code=422, detail="All 25 assessment questions must be answered exactly once")

    domain_scores: dict[str, list[int]] = {}
    for question in QUESTION_BANK:
        domain_scores.setdefault(question["domain"], []).append(100 if answer_map[question["id"]] == question["correct"] else 0)
    skill_scores = {domain: round(sum(scores) / len(scores)) for domain, scores in domain_scores.items()}
    readiness = round(sum(skill_scores.values()) / len(skill_scores))
    gaps = [question["skill"] for question in QUESTION_BANK if answer_map[question["id"]] != question["correct"]]
    unique_gaps = list(dict.fromkeys(gaps))[:5]
    recommendations = [f"Complete the {gap} learning module" for gap in unique_gaps]
    result = {"id": str(uuid4()), "user_id": user["id"], "readiness": readiness, "skill_scores": skill_scores, "gaps": unique_gaps, "recommendations": recommendations, "completed_at": datetime.now(timezone.utc)}
    await get_pool().execute(
        "INSERT INTO assessment_results (id,user_id,readiness,skill_scores,gaps,recommendations,completed_at) VALUES ($1,$2,$3,$4,$5,$6,$7)",
        result["id"], user["id"], readiness, skill_scores, unique_gaps, recommendations, result["completed_at"],
    )
    await get_pool().execute("UPDATE users SET readiness=$1,updated_at=$2 WHERE id=$3", readiness, datetime.now(timezone.utc), user["id"])
    return AssessmentResult(**{key: result[key] for key in AssessmentResult.model_fields})