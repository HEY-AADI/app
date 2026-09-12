from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends

from lib.db import get_pool
from models.assessment import AssessmentQuestion, AssessmentResult, AssessmentStartResponse, AssessmentSubmit
from routers.auth import get_current_user

router = APIRouter(prefix="/assessments", tags=["assessments"])

QUESTION_BANK = [
    {"id": "clinical-1", "prompt": "Which action best supports safe Panchakarma preparation?", "domain": "Clinical skills", "skill": "Panchakarma", "options": ["Skip patient history", "Confirm assessment and contraindications", "Use one protocol for everyone", "Avoid documenting observations"], "correct": 1, "difficulty": 1},
    {"id": "clinical-2", "prompt": "A patient reports discomfort during a supervised procedure. What is the best first response?", "domain": "Clinical skills", "skill": "Patient communication", "options": ["Continue silently", "Pause, listen and escalate appropriately", "Ask them to tolerate it", "End the record"], "correct": 1, "difficulty": 2},
    {"id": "knowledge-1", "prompt": "What is the purpose of a standard operating procedure?", "domain": "AYUSH knowledge", "skill": "Process knowledge", "options": ["Create repeatable, documented practice", "Replace all judgement", "Reduce supervision", "Hide variation"], "correct": 0, "difficulty": 1},
    {"id": "knowledge-2", "prompt": "Which statement best describes evidence-informed AYUSH practice?", "domain": "AYUSH knowledge", "skill": "Evidence literacy", "options": ["Only tradition matters", "Use relevant evidence with clinical context", "Avoid recording outcomes", "Copy every published protocol"], "correct": 1, "difficulty": 2},
    {"id": "communication-1", "prompt": "A clear handover should include:", "domain": "Communication", "skill": "Team collaboration", "options": ["Only a conclusion", "Relevant context, action and risk", "Personal opinion only", "No written follow-up"], "correct": 1, "difficulty": 1},
    {"id": "communication-2", "prompt": "How should you respond when a mentor gives unclear feedback?", "domain": "Communication", "skill": "Feedback literacy", "options": ["Ignore it", "Ask for a concrete example and next step", "Defend every decision", "Wait until completion"], "correct": 1, "difficulty": 2},
    {"id": "digital-1", "prompt": "Which practice improves the quality of a digital clinical record?", "domain": "Digital skills", "skill": "Documentation", "options": ["Use shared passwords", "Record timely, structured observations", "Copy forward everything", "Delete inconvenient notes"], "correct": 1, "difficulty": 1},
    {"id": "digital-2", "prompt": "A spreadsheet shows an unexpected outlier. What should you do first?", "domain": "Digital skills", "skill": "Data literacy", "options": ["Delete the row", "Check the source and definition", "Average it away", "Publish immediately"], "correct": 1, "difficulty": 2},
    {"id": "industry-1", "prompt": "What does GMP primarily help an organisation control?", "domain": "Industry readiness", "skill": "GMP fundamentals", "options": ["Brand colour", "Consistent quality and process control", "Recruitment only", "Social media reach"], "correct": 1, "difficulty": 1},
    {"id": "industry-2", "prompt": "Which is strongest evidence of quality documentation skill?", "domain": "Industry readiness", "skill": "Quality documentation", "options": ["A self-rating", "A reviewed workflow with traceable sources", "A job title alone", "An unlabelled screenshot"], "correct": 1, "difficulty": 2},
    {"id": "industry-3", "prompt": "A production process changes. What should happen to its SOP?", "domain": "Industry readiness", "skill": "Quality assurance", "options": ["Nothing", "Review, version and retrain as needed", "Delete old evidence", "Wait for an audit"], "correct": 1, "difficulty": 3},
    {"id": "research-1", "prompt": "A useful research question is:", "domain": "Research", "skill": "Research methods", "options": ["Broad and impossible to measure", "Specific, answerable and relevant", "Based only on assumptions", "Changed after every result"], "correct": 1, "difficulty": 1},
]


@router.get("/questions", response_model=list[AssessmentQuestion])
async def get_questions(user: dict = Depends(get_current_user)):
    return [AssessmentQuestion(**{key: question[key] for key in AssessmentQuestion.model_fields}) for question in QUESTION_BANK]


@router.get("/start", response_model=AssessmentStartResponse)
async def start_assessment(user: dict = Depends(get_current_user)):
    return AssessmentStartResponse(session_id=str(uuid4()), questions=[AssessmentQuestion(**{key: question[key] for key in AssessmentQuestion.model_fields}) for question in QUESTION_BANK])


@router.get("/latest", response_model=AssessmentResult | None)
async def get_latest(user: dict = Depends(get_current_user)):
    document_row = await get_pool().fetchrow("SELECT id,readiness,skill_scores,gaps,recommendations,completed_at FROM assessment_results WHERE user_id=$1 ORDER BY completed_at DESC LIMIT 1", user["id"])
    document = dict(document_row) if document_row else None
    if not document:
        return None
    return AssessmentResult(**{key: document[key] for key in AssessmentResult.model_fields})


@router.post("/submit", response_model=AssessmentResult)
async def submit_assessment(payload: AssessmentSubmit, user: dict = Depends(get_current_user)):
    answer_map = {answer.question_id: answer.option_index for answer in payload.answers}
    domain_scores: dict[str, list[int]] = {}
    for question in QUESTION_BANK:
        domain_scores.setdefault(question["domain"], []).append(100 if answer_map.get(question["id"]) == question["correct"] else 0)
    skill_scores = {domain: round(sum(scores) / len(scores)) for domain, scores in domain_scores.items()}
    readiness = round(sum(skill_scores.values()) / len(skill_scores))
    gaps = [question["skill"] for question in QUESTION_BANK if answer_map.get(question["id"]) != question["correct"]]
    unique_gaps = list(dict.fromkeys(gaps))[:4]
    recommendations = [f"Complete the {gap} learning module" for gap in unique_gaps]
    result = {"id": str(uuid4()), "user_id": user["id"], "readiness": readiness, "skill_scores": skill_scores, "gaps": unique_gaps, "recommendations": recommendations, "completed_at": datetime.now(timezone.utc)}
    await get_pool().execute("INSERT INTO assessment_results (id,user_id,readiness,skill_scores,gaps,recommendations,completed_at) VALUES ($1,$2,$3,$4,$5,$6,$7)", result["id"], user["id"], readiness, skill_scores, unique_gaps, recommendations, result["completed_at"])
    await get_pool().execute("UPDATE users SET readiness=$1,updated_at=$2 WHERE id=$3", readiness, datetime.now(timezone.utc), user["id"])
    return AssessmentResult(**{key: result[key] for key in AssessmentResult.model_fields})