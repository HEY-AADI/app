from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from lib.db import get_pool
from models.opportunities import ApplicationOut, InternshipOut, MilestoneUpdate, OpportunityOut
from routers.auth import get_current_user

router = APIRouter(tags=["opportunities"])


def _opportunity(document: dict) -> OpportunityOut:
    return OpportunityOut(**{key: document[key] for key in OpportunityOut.model_fields})


@router.get("/opportunities", response_model=list[OpportunityOut])
async def list_opportunities():
    rows = await get_pool().fetch("SELECT id,type,title,organisation,location,system,mode,stipend,duration,match,skills,gaps,verified,mentor,deliverable,deadline FROM opportunities ORDER BY match DESC LIMIT 100")
    return [_opportunity(dict(row)) for row in rows]


@router.get("/opportunities/{opportunity_id}", response_model=OpportunityOut)
async def get_opportunity(opportunity_id: str):
    row = await get_pool().fetchrow("SELECT id,type,title,organisation,location,system,mode,stipend,duration,match,skills,gaps,verified,mentor,deliverable,deadline FROM opportunities WHERE id=$1", opportunity_id)
    document = dict(row) if row else None
    if not document:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return _opportunity(document)


@router.post("/opportunities/{opportunity_id}/apply", response_model=ApplicationOut, status_code=201)
async def apply_to_opportunity(opportunity_id: str, user: dict = Depends(get_current_user)):
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only student accounts can apply")
    opportunity_row = await get_pool().fetchrow(
        "SELECT id,title,organisation,mentor,deliverable FROM opportunities WHERE id=$1",
        opportunity_id,
    )
    opportunity = dict(opportunity_row) if opportunity_row else None
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    existing_row = await get_pool().fetchrow("SELECT id,opportunity_id,opportunity_title,organisation,status,next_action,applied_at FROM applications WHERE user_id=$1 AND opportunity_id=$2", user["id"], opportunity_id)
    existing = dict(existing_row) if existing_row else None
    if existing:
        return ApplicationOut(**{key: existing[key] for key in ApplicationOut.model_fields})
    application = {
        "id": str(uuid4()),
        "user_id": user["id"],
        "opportunity_id": opportunity_id,
        "opportunity_title": opportunity["title"],
        "organisation": opportunity["organisation"],
        "status": "Applied",
        "next_action": "Complete your profile while the employer reviews your application.",
        "applied_at": datetime.now(timezone.utc),
    }
    await get_pool().execute("INSERT INTO applications (id,user_id,opportunity_id,opportunity_title,organisation,status,next_action,applied_at) VALUES ($1,$2,$3,$4,$5,$6,$7,$8)", application["id"], application["user_id"], application["opportunity_id"], application["opportunity_title"], application["organisation"], application["status"], application["next_action"], application["applied_at"])
    milestones = [
        {"id": "applied", "title": "Application submitted", "detail": "Your application is under review.", "status": "active", "date": "Today"},
        {"id": "mentor", "title": "Mentor assigned", "detail": "A named mentor is assigned after selection.", "status": "upcoming", "date": "Next"},
        {"id": "deliverable", "title": "Deliverable defined", "detail": opportunity["deliverable"], "status": "upcoming", "date": "Later"},
        {"id": "evidence", "title": "Evidence pack", "detail": "Verified experience after completion.", "status": "upcoming", "date": "Later"},
    ]
    await get_pool().execute("INSERT INTO internships (id,user_id,application_id,opportunity_title,organisation,week,total_weeks,mentor,deliverable,divergence_alert,milestones) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)", str(uuid4()), user["id"], application["id"], opportunity["title"], opportunity["organisation"], 0, 8, opportunity["mentor"], opportunity["deliverable"], False, milestones)
    return ApplicationOut(**application)


@router.get("/applications/me", response_model=list[ApplicationOut])
async def my_applications(user: dict = Depends(get_current_user)):
    rows = await get_pool().fetch("SELECT id,opportunity_id,opportunity_title,organisation,status,next_action,applied_at FROM applications WHERE user_id=$1 ORDER BY applied_at DESC LIMIT 100", user["id"])
    return [ApplicationOut(**dict(row)) for row in rows]


@router.get("/internships/me", response_model=list[InternshipOut])
async def my_internships(user: dict = Depends(get_current_user)):
    rows = await get_pool().fetch("SELECT id,application_id,opportunity_title,organisation,week,total_weeks,mentor,deliverable,divergence_alert,milestones FROM internships WHERE user_id=$1 ORDER BY week DESC,id LIMIT 100", user["id"])
    return [InternshipOut(**dict(row)) for row in rows]


@router.patch("/internships/{internship_id}/milestones", response_model=InternshipOut)
async def update_milestone(internship_id: str, payload: MilestoneUpdate, user: dict = Depends(get_current_user)):
    row = await get_pool().fetchrow("SELECT id,application_id,opportunity_title,organisation,week,total_weeks,mentor,deliverable,divergence_alert,milestones FROM internships WHERE id=$1 AND user_id=$2", internship_id, user["id"])
    internship = dict(row) if row else None
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")
    milestones = internship["milestones"]
    if not any(item["id"] == payload.milestone_id for item in milestones):
        raise HTTPException(status_code=404, detail="Milestone not found")
    for item in milestones:
        if item["id"] == payload.milestone_id:
            item["status"] = payload.status
    await get_pool().execute("UPDATE internships SET milestones=$1 WHERE id=$2", milestones, internship_id)
    internship["milestones"] = milestones
    return InternshipOut(**internship)