from typing import Literal

from pydantic import BaseModel, Field


OpportunityType = Literal["Internship", "Job", "Project"]
WorkMode = Literal["Hybrid", "On-site", "Remote"]
ApplicationStage = Literal["Applied", "Under Review", "Shortlisted", "Interview", "Selected", "Rejected"]


class EmployerOpportunityCreate(BaseModel):
    type: OpportunityType
    title: str = Field(min_length=3, max_length=120)
    system: str = Field(min_length=2, max_length=80)
    skills: list[str] = Field(min_length=1, max_length=15)
    eligibility: str = Field(min_length=3, max_length=300)
    stipend: str = Field(min_length=1, max_length=80)
    location: str = Field(min_length=2, max_length=120)
    mode: WorkMode
    duration: str = Field(min_length=2, max_length=80)
    mentor: str = Field(min_length=2, max_length=120)
    deliverable: str = Field(min_length=10, max_length=500)
    accessibility: str = Field(min_length=3, max_length=300)
    deadline: str = Field(min_length=3, max_length=80)


class EmployerOpportunityOut(EmployerOpportunityCreate):
    id: str
    organisation: str
    publication_status: Literal["draft", "published"]
    application_count: int = 0


class ApplicationStageUpdate(BaseModel):
    status: ApplicationStage


class CandidateOut(BaseModel):
    application_id: str
    opportunity_id: str
    candidate_code: str
    status: ApplicationStage | Literal["Joined", "Completed"]
    readiness: int
    skills: list[dict]
    evidence_count: int
    name: str | None = None
    email: str | None = None
    institution: str | None = None
    identity_revealed: bool
    institution_revealed: bool