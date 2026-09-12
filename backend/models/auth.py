from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Role = Literal["student", "employer", "alumni", "institution", "ministry"]


class UserPublic(BaseModel):
    id: str
    email: str
    name: str
    role: Role
    institution: str | None = None
    readiness: int = 0


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)


class SessionResponse(BaseModel):
    user: UserPublic