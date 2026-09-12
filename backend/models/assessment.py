from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class AssessmentQuestion(BaseModel):
    id: str
    prompt: str
    domain: str
    skill: str
    options: list[str]
    difficulty: int = Field(ge=1, le=3)
    question_type: Literal["mcq", "assertion_reasoning", "case_based", "scenario_based"] = "mcq"
    context: str | None = None


class AssessmentAnswer(BaseModel):
    question_id: str
    option_index: int = Field(ge=0, le=3)


class AssessmentSubmit(BaseModel):
    answers: list[AssessmentAnswer]


class AssessmentStartResponse(BaseModel):
    session_id: str
    questions: list[AssessmentQuestion]


class AssessmentResult(BaseModel):
    id: str
    readiness: int
    skill_scores: dict[str, int]
    gaps: list[str]
    recommendations: list[str]
    completed_at: datetime