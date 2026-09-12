from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SkillEntry(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    level: int = Field(ge=0, le=100)
    provenance: Literal["Self-declared", "Institution verified", "Employer verified", "Issuer verified"]
    evidence: str = Field(default="", max_length=240)


class PortfolioEvidence(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    issuer: str = Field(min_length=2, max_length=120)
    evidence_type: Literal["Project", "Internship", "Certification", "Assessment"]
    date: str


class StudentProfileUpdate(BaseModel):
    education: str = Field(min_length=2, max_length=120)
    ayush_system: Literal["Ayurveda", "Siddha", "Unani", "Homoeopathy", "Yoga & Naturopathy"]
    graduation_year: int = Field(ge=2020, le=2040)
    interests: list[str] = Field(max_length=10)
    skills: list[SkillEntry] = Field(max_length=20)
    portfolio_evidence: list[PortfolioEvidence] = Field(max_length=20)


class StudentProfileOut(StudentProfileUpdate):
    user_id: str
    name: str
    email: str
    institution: str | None = None
    updated_at: datetime