import base64
from datetime import datetime, timezone
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException

from lib.db import get_pool
from models.profile import CareerPassportDocument, StudentProfileOut, StudentProfileUpdate
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


@router.get("/passport", response_model=CareerPassportDocument)
async def download_passport(user: dict = Depends(get_current_user)):
    _require_student(user)
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    profile_row = await get_pool().fetchrow("SELECT * FROM student_profiles WHERE user_id=$1", user["id"])
    if not profile_row:
        raise HTTPException(status_code=404, detail="Student profile not found")
    profile = dict(profile_row)
    assessment = await get_pool().fetchrow("SELECT readiness,skill_scores FROM assessment_results WHERE user_id=$1 ORDER BY completed_at DESC LIMIT 1", user["id"])
    internships = await get_pool().fetch("SELECT opportunity_title,organisation,week,total_weeks,mentor,deliverable FROM internships WHERE user_id=$1 ORDER BY week DESC", user["id"])

    stream = BytesIO()
    page = canvas.Canvas(stream, pagesize=A4)
    width, height = A4
    page.setFillColor(HexColor("#174A3A"))
    page.rect(0, height - 105, width, 105, fill=1, stroke=0)
    page.setFillColorRGB(1, 1, 1)
    page.setFont("Helvetica-Bold", 22)
    page.drawString(42, height - 52, "SAMANVAYA CAREER PASSPORT")
    page.setFont("Helvetica", 9)
    page.drawString(42, height - 74, "Portable profile preview · evidence provenance visible")
    page.setFillColor(HexColor("#111827"))
    y = height - 145
    page.setFont("Helvetica-Bold", 20)
    page.drawString(42, y, user["name"])
    page.setFont("Helvetica", 10)
    page.drawString(42, y - 20, f"{profile['education']} · {profile['ayush_system']} · Graduating {profile['graduation_year']}")
    page.drawString(42, y - 36, user.get("institution") or "Institution not added")
    readiness = assessment["readiness"] if assessment else user.get("readiness", 0)
    page.setFillColor(HexColor("#C58B2A"))
    page.setFont("Helvetica-Bold", 28)
    page.drawRightString(width - 42, y, f"{readiness}%")
    page.setFont("Helvetica", 9)
    page.drawRightString(width - 42, y - 18, "Career readiness")
    y -= 78
    page.setFillColor(HexColor("#111827"))
    page.setFont("Helvetica-Bold", 13)
    page.drawString(42, y, "VERIFIED SKILLS & EVIDENCE")
    y -= 24
    for skill in profile["skills"][:8]:
        page.setFont("Helvetica-Bold", 10)
        page.drawString(50, y, f"{skill['name']}  ·  {skill['level']}%")
        page.setFont("Helvetica", 8)
        page.drawString(275, y, f"{skill['provenance']}  |  {skill['evidence'] or 'Evidence not added'}")
        y -= 19
    y -= 10
    page.setFont("Helvetica-Bold", 13)
    page.drawString(42, y, "EXPERIENCE")
    y -= 24
    if internships:
        for internship in internships[:4]:
            page.setFont("Helvetica-Bold", 10)
            page.drawString(50, y, internship["opportunity_title"])
            page.setFont("Helvetica", 8)
            page.drawString(260, y, f"{internship['organisation']} · Week {internship['week']} of {internship['total_weeks']}")
            y -= 17
            page.drawString(50, y, f"Mentor: {internship['mentor']} · Deliverable: {internship['deliverable'][:70]}")
            y -= 23
    else:
        page.setFont("Helvetica", 9)
        page.drawString(50, y, "No internship evidence recorded yet.")
        y -= 22
    page.setFont("Helvetica-Bold", 13)
    page.drawString(42, y, "PORTFOLIO")
    y -= 22
    page.setFont("Helvetica", 9)
    for item in profile["portfolio_evidence"][:6]:
        page.drawString(50, y, f"{item['title']} · {item['evidence_type']} · {item['issuer']} · {item['date']}")
        y -= 17
    page.setFillColor(HexColor("#6B7280"))
    page.setFont("Helvetica", 8)
    page.drawString(42, 42, "SAMANVAYA prototype · Not an official government credential · Verify evidence with the listed issuer")
    page.showPage()
    page.save()
    return CareerPassportDocument(filename="samanvaya-career-passport.pdf", media_type="application/pdf", content_base64=base64.b64encode(stream.getvalue()).decode("ascii"))