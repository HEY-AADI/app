from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class OpportunityOut(BaseModel):
    id: str
    type: Literal["Internship", "Job", "Project"]
    title: str
    organisation: str
    location: str
    system: str
    mode: Literal["Hybrid", "On-site", "Remote"]
    stipend: str
    duration: str
    match: int
    skills: list[str]
    gaps: list[str]
    verified: bool
    mentor: str
    deliverable: str
    deadline: str


class ApplicationOut(BaseModel):
    id: str
    opportunity_id: str
    opportunity_title: str
    organisation: str
    status: Literal["Applied", "Under Review", "Shortlisted", "Interview", "Selected", "Joined", "Completed", "Rejected"]
    next_action: str
    applied_at: datetime


class MilestoneOut(BaseModel):
    id: str
    title: str
    detail: str
    status: Literal["complete", "active", "upcoming"]
    date: str


class InternshipOut(BaseModel):
    id: str
    application_id: str
    opportunity_title: str
    organisation: str
    week: int
    total_weeks: int
    mentor: str
    deliverable: str
    divergence_alert: bool
    milestones: list[MilestoneOut]


class MilestoneUpdate(BaseModel):
    milestone_id: str
    status: Literal["complete", "active", "upcoming"]