from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from lib.db import get_pool
from models.karma import CheckInCreate, CheckInOut, CheckInSummary, EvidencePackOut
from routers.auth import get_current_user

router = APIRouter(prefix="/internships", tags=["karma"])


async def _internship_for_user(internship_id: str, user: dict) -> dict:
    row = await get_pool().fetchrow(
        "SELECT id,user_id,opportunity_title,organisation,week,total_weeks,mentor,deliverable,divergence_alert FROM internships WHERE id=$1",
        internship_id,
    )
    internship = dict(row) if row else None
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")
    if user["role"] == "student" and internship["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Internship access denied")
    if user["role"] not in {"student", "alumni", "institution"}:
        raise HTTPException(status_code=403, detail="Internship access denied")
    return internship


async def _summary(internship_id: str, week: int) -> CheckInSummary:
    rows = await get_pool().fetch(
        "SELECT id,internship_id,week,actor,meeting_frequency,useful_feedback,reflection,created_at FROM internship_checkins WHERE internship_id=$1 AND week=$2",
        internship_id, week,
    )
    checkins = {row["actor"]: CheckInOut(**dict(row)) for row in rows}
    student = checkins.get("student")
    mentor = checkins.get("mentor")
    divergence = bool(student and mentor and (
        student.meeting_frequency != mentor.meeting_frequency
        or (student.useful_feedback == "No" and mentor.useful_feedback == "Yes")
    ))
    await get_pool().execute("UPDATE internships SET divergence_alert=$1 WHERE id=$2", divergence, internship_id)
    return CheckInSummary(internship_id=internship_id, week=week, student=student, mentor=mentor, divergence_alert=divergence)


@router.get("/{internship_id}/check-ins", response_model=CheckInSummary)
async def get_check_ins(internship_id: str, week: int = 4, user: dict = Depends(get_current_user)):
    await _internship_for_user(internship_id, user)
    return await _summary(internship_id, week)


@router.post("/{internship_id}/check-ins", response_model=CheckInSummary)
async def save_check_in(internship_id: str, payload: CheckInCreate, user: dict = Depends(get_current_user)):
    await _internship_for_user(internship_id, user)
    actor = "student" if user["role"] == "student" else "mentor"
    await get_pool().execute(
        """INSERT INTO internship_checkins (id,internship_id,week,actor,meeting_frequency,useful_feedback,reflection,created_at)
           VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
           ON CONFLICT (internship_id,week,actor) DO UPDATE SET meeting_frequency=EXCLUDED.meeting_frequency,
           useful_feedback=EXCLUDED.useful_feedback,reflection=EXCLUDED.reflection,created_at=EXCLUDED.created_at""",
        str(uuid4()), internship_id, payload.week, actor, payload.meeting_frequency,
        payload.useful_feedback, payload.reflection, datetime.now(timezone.utc),
    )
    return await _summary(internship_id, payload.week)


@router.get("/{internship_id}/evidence-pack", response_model=EvidencePackOut)
async def get_evidence_pack(internship_id: str, user: dict = Depends(get_current_user)):
    internship = await _internship_for_user(internship_id, user)
    rows = await get_pool().fetch(
        "SELECT actor,reflection,useful_feedback FROM internship_checkins WHERE internship_id=$1 ORDER BY created_at DESC",
        internship_id,
    )
    checkins = {row["actor"]: dict(row) for row in rows}
    return EvidencePackOut(
        internship_id=internship_id,
        opportunity_title=internship["opportunity_title"],
        organisation=internship["organisation"],
        deliverable=internship["deliverable"],
        performance_metric="Milestones and check-ins recorded through the SAMANVAYA internship workflow.",
        mentor_assessment=checkins.get("mentor", {}).get("reflection", "Mentor evaluation pending."),
        student_reflection=checkins.get("student", {}).get("reflection", "Student reflection pending."),
        completion_status=f"Week {internship['week']} of {internship['total_weeks']} · evidence pack preview",
        generated_at=datetime.now(timezone.utc),
    )