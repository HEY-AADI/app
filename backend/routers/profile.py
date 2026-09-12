from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from lib.db import get_pool
from models.profile import StudentProfileOut, StudentProfileUpdate
from routers.auth import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])


def _require_student(user: dict) -> None:
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Student profile access required")


@router.get("/me", response_model=StudentProfileOut)
async def get_profile(user: dict = Depends(get_current_user)):
    _require_student(user)
    row = await get_pool().fetchrow(
        """SELECT p.user_id,u.name,u.email,u.institution,p.education,p.ayush_system,p.graduation_year,
                  p.interests,p.skills,p.portfolio_evidence,p.updated_at
           FROM student_profiles p JOIN users u ON u.id=p.user_id WHERE p.user_id=$1""",
        user["id"],
    )
    if not row:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return StudentProfileOut(**dict(row))


@router.patch("/me", response_model=StudentProfileOut)
async def update_profile(payload: StudentProfileUpdate, user: dict = Depends(get_current_user)):
    _require_student(user)
    updated_at = datetime.now(timezone.utc)
    await get_pool().execute(
        """INSERT INTO student_profiles (user_id,education,ayush_system,graduation_year,interests,skills,portfolio_evidence,updated_at)
           VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
           ON CONFLICT (user_id) DO UPDATE SET education=EXCLUDED.education,ayush_system=EXCLUDED.ayush_system,
           graduation_year=EXCLUDED.graduation_year,interests=EXCLUDED.interests,skills=EXCLUDED.skills,
           portfolio_evidence=EXCLUDED.portfolio_evidence,updated_at=EXCLUDED.updated_at""",
        user["id"], payload.education, payload.ayush_system, payload.graduation_year,
        payload.interests, [item.model_dump() for item in payload.skills],
        [item.model_dump() for item in payload.portfolio_evidence], updated_at,
    )
    return StudentProfileOut(
        user_id=user["id"], name=user["name"], email=user["email"], institution=user.get("institution"),
        updated_at=updated_at, **payload.model_dump(),
    )