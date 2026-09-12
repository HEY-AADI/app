from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from lib.db import get_pool
from models.employer import ApplicationStageUpdate, CandidateOut, EmployerOpportunityCreate, EmployerOpportunityOut
from routers.auth import get_current_user

router = APIRouter(prefix="/employer", tags=["employer"])


def _require_employer(user: dict) -> None:
    if user["role"] != "employer":
        raise HTTPException(status_code=403, detail="Employer access required")


def _opportunity(row: dict) -> EmployerOpportunityOut:
    return EmployerOpportunityOut(**dict(row))


@router.get("/opportunities", response_model=list[EmployerOpportunityOut])
async def list_employer_opportunities(user: dict = Depends(get_current_user)):
    _require_employer(user)
    rows = await get_pool().fetch(
        """SELECT o.id,o.type,o.title,o.organisation,o.system,o.skills,o.eligibility,o.stipend,o.location,o.mode,
                  o.duration,o.mentor,o.deliverable,o.accessibility,o.deadline,o.publication_status,
                  COUNT(a.id)::int AS application_count
           FROM opportunities o LEFT JOIN applications a ON a.opportunity_id=o.id
           WHERE o.created_by=$1 GROUP BY o.id ORDER BY o.title""",
        user["id"],
    )
    return [_opportunity(dict(row)) for row in rows]


@router.post("/opportunities", response_model=EmployerOpportunityOut, status_code=201)
async def create_draft(payload: EmployerOpportunityCreate, user: dict = Depends(get_current_user)):
    _require_employer(user)
    opportunity_id = str(uuid4())
    await get_pool().execute(
        """INSERT INTO opportunities (id,type,title,organisation,location,system,mode,stipend,duration,match,skills,gaps,verified,mentor,deliverable,deadline,eligibility,accessibility,created_by,publication_status)
           VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,0,$10,'[]'::jsonb,FALSE,$11,$12,$13,$14,$15,$16,'draft')""",
        opportunity_id, payload.type, payload.title, user["name"], payload.location, payload.system,
        payload.mode, payload.stipend, payload.duration, payload.skills, payload.mentor,
        payload.deliverable, payload.deadline, payload.eligibility, payload.accessibility, user["id"],
    )
    return EmployerOpportunityOut(id=opportunity_id, organisation=user["name"], publication_status="draft", application_count=0, **payload.model_dump())


@router.post("/opportunities/{opportunity_id}/publish", response_model=EmployerOpportunityOut)
async def publish_opportunity(opportunity_id: str, user: dict = Depends(get_current_user)):
    _require_employer(user)
    row = await get_pool().fetchrow("SELECT * FROM opportunities WHERE id=$1 AND created_by=$2", opportunity_id, user["id"])
    if not row:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    opportunity = dict(row)
    if opportunity["type"] == "Internship" and (not opportunity["mentor"].strip() or not opportunity["deliverable"].strip() or not opportunity["stipend"].strip()):
        raise HTTPException(status_code=422, detail="Internships require a mentor, deliverable and disclosed stipend")
    await get_pool().execute("UPDATE opportunities SET publication_status='published' WHERE id=$1", opportunity_id)
    opportunity["publication_status"] = "published"
    count = await get_pool().fetchval("SELECT COUNT(*) FROM applications WHERE opportunity_id=$1", opportunity_id)
    return EmployerOpportunityOut(application_count=count, **opportunity)


@router.get("/opportunities/{opportunity_id}/candidates", response_model=list[CandidateOut])
async def list_candidates(opportunity_id: str, user: dict = Depends(get_current_user)):
    _require_employer(user)
    owns = await get_pool().fetchval("SELECT EXISTS(SELECT 1 FROM opportunities WHERE id=$1 AND created_by=$2)", opportunity_id, user["id"])
    if not owns:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    rows = await get_pool().fetch(
        """SELECT a.id AS application_id,a.opportunity_id,a.status,a.user_id,u.name,u.email,u.institution,u.readiness,
                  COALESCE(p.skills,'[]'::jsonb) AS skills,COALESCE(jsonb_array_length(p.portfolio_evidence),0)::int AS evidence_count
           FROM applications a JOIN users u ON u.id=a.user_id LEFT JOIN student_profiles p ON p.user_id=u.id
           WHERE a.opportunity_id=$1 ORDER BY a.applied_at""",
        opportunity_id,
    )
    candidates = []
    for row in rows:
        item = dict(row)
        identity_revealed = item["status"] in {"Shortlisted", "Interview", "Selected", "Joined", "Completed"}
        institution_revealed = item["status"] in {"Interview", "Selected", "Joined", "Completed"}
        candidates.append(CandidateOut(
            application_id=item["application_id"], opportunity_id=item["opportunity_id"],
            candidate_code=f"AYU-{item['user_id'][-6:].upper()}", status=item["status"], readiness=item["readiness"],
            skills=item["skills"], evidence_count=item["evidence_count"],
            name=item["name"] if identity_revealed else None, email=item["email"] if identity_revealed else None,
            institution=item["institution"] if institution_revealed else None,
            identity_revealed=identity_revealed, institution_revealed=institution_revealed,
        ))
    return candidates


@router.patch("/applications/{application_id}", response_model=CandidateOut)
async def update_candidate_stage(application_id: str, payload: ApplicationStageUpdate, user: dict = Depends(get_current_user)):
    _require_employer(user)
    row = await get_pool().fetchrow(
        """SELECT a.id,a.opportunity_id FROM applications a JOIN opportunities o ON o.id=a.opportunity_id
           WHERE a.id=$1 AND o.created_by=$2""",
        application_id, user["id"],
    )
    if not row:
        raise HTTPException(status_code=404, detail="Application not found")
    await get_pool().execute("UPDATE applications SET status=$1,next_action=$2 WHERE id=$3", payload.status, f"Employer moved this application to {payload.status}.", application_id)
    candidates = await list_candidates(row["opportunity_id"], user)
    return next(candidate for candidate in candidates if candidate.application_id == application_id)