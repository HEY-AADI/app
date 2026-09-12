from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import List
import os

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware

from lib.db import close_database, get_pool, init_database
from routers.assessments import router as assessments_router
from routers.auth import router as auth_router
from routers.opportunities import router as opportunities_router
from routers.profile import router as profile_router
from routers.karma import router as karma_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_database()
    yield
    await close_database()


app = FastAPI(lifespan=lifespan, title="SAMANVAYA API")
api_router = APIRouter(prefix="/api")


class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: __import__("uuid").uuid4().hex)
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StatusCheckCreate(BaseModel):
    client_name: str


@api_router.get("/")
async def root():
    return {"message": "SAMANVAYA API ready", "persistence": "PostgreSQL"}


@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_obj = StatusCheck(client_name=input.client_name)
    await get_pool().execute("INSERT INTO status_checks (id,client_name,timestamp) VALUES ($1,$2,$3)", status_obj.id, status_obj.client_name, status_obj.timestamp)
    return status_obj


@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    rows = await get_pool().fetch("SELECT id,client_name,timestamp FROM status_checks ORDER BY timestamp DESC LIMIT 1000")
    return [StatusCheck(**dict(row)) for row in rows]


api_router.include_router(auth_router)
api_router.include_router(opportunities_router)
api_router.include_router(assessments_router)
api_router.include_router(profile_router)
api_router.include_router(karma_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)