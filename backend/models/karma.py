from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class CheckInCreate(BaseModel):
    week: int = Field(ge=1, le=52)
    meeting_frequency: Literal["Never", "Once", "Weekly"]
    useful_feedback: Literal["Yes", "Partially", "No"]
    reflection: str = Field(min_length=3, max_length=500)


class CheckInOut(CheckInCreate):
    id: str
    internship_id: str
    actor: Literal["student", "mentor"]
    created_at: datetime


class CheckInSummary(BaseModel):
    internship_id: str
    week: int
    student: CheckInOut | None = None
    mentor: CheckInOut | None = None
    divergence_alert: bool


class EvidencePackOut(BaseModel):
    internship_id: str
    opportunity_title: str
    organisation: str
    deliverable: str
    performance_metric: str
    mentor_assessment: str
    student_reflection: str
    completion_status: str
    generated_at: datetime