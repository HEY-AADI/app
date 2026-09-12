"""Small async PostgreSQL boundary for the Phase 2 prototype."""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import asyncpg
from dotenv import load_dotenv

from lib.security import hash_password

load_dotenv(Path(__file__).parent.parent / ".env")

logger = logging.getLogger(__name__)
_pool: asyncpg.Pool | None = None


async def _init_connection(connection: asyncpg.Connection) -> None:
    await connection.set_type_codec("json", encoder=json.dumps, decoder=json.loads, schema="pg_catalog")
    await connection.set_type_codec("jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog")


async def connect_database() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        dsn = os.environ["DATABASE_URL"]
        _pool = await asyncpg.create_pool(dsn=dsn, min_size=1, max_size=5, init=_init_connection)
    return _pool


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Database pool is not ready")
    return _pool


async def init_schema() -> None:
    pool = get_pool()
    await pool.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY, email TEXT NOT NULL UNIQUE, name TEXT NOT NULL,
            role TEXT NOT NULL, institution TEXT, readiness INTEGER NOT NULL DEFAULT 0,
            password_hash TEXT NOT NULL, updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMPTZ NOT NULL, expires_at TIMESTAMPTZ NOT NULL
        );
        CREATE INDEX IF NOT EXISTS sessions_expiry_idx ON sessions(expires_at);
        CREATE TABLE IF NOT EXISTS opportunities (
            id TEXT PRIMARY KEY, type TEXT NOT NULL, title TEXT NOT NULL, organisation TEXT NOT NULL,
            location TEXT NOT NULL, system TEXT NOT NULL, mode TEXT NOT NULL, stipend TEXT NOT NULL,
            duration TEXT NOT NULL, match INTEGER NOT NULL, skills JSONB NOT NULL, gaps JSONB NOT NULL,
            verified BOOLEAN NOT NULL, mentor TEXT NOT NULL, deliverable TEXT NOT NULL, deadline TEXT NOT NULL
        );
        ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS eligibility TEXT NOT NULL DEFAULT 'Relevant AYUSH qualification';
        ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS accessibility TEXT NOT NULL DEFAULT 'Contact the employer for accessibility information';
        ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS created_by TEXT REFERENCES users(id) ON DELETE SET NULL;
        ALTER TABLE opportunities ADD COLUMN IF NOT EXISTS publication_status TEXT NOT NULL DEFAULT 'published';
        CREATE INDEX IF NOT EXISTS opportunities_match_idx ON opportunities(match DESC);
        CREATE TABLE IF NOT EXISTS applications (
            id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            opportunity_id TEXT NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
            opportunity_title TEXT NOT NULL, organisation TEXT NOT NULL, status TEXT NOT NULL,
            next_action TEXT NOT NULL, applied_at TIMESTAMPTZ NOT NULL,
            UNIQUE(user_id, opportunity_id)
        );
        CREATE INDEX IF NOT EXISTS applications_user_idx ON applications(user_id, applied_at DESC);
        CREATE TABLE IF NOT EXISTS internships (
            id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            application_id TEXT NOT NULL UNIQUE REFERENCES applications(id) ON DELETE CASCADE,
            opportunity_title TEXT NOT NULL, organisation TEXT NOT NULL, week INTEGER NOT NULL,
            total_weeks INTEGER NOT NULL, mentor TEXT NOT NULL, deliverable TEXT NOT NULL,
            divergence_alert BOOLEAN NOT NULL DEFAULT FALSE, milestones JSONB NOT NULL
        );
        CREATE TABLE IF NOT EXISTS assessment_results (
            id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            readiness INTEGER NOT NULL, skill_scores JSONB NOT NULL, gaps JSONB NOT NULL,
            recommendations JSONB NOT NULL, completed_at TIMESTAMPTZ NOT NULL
        );
        CREATE INDEX IF NOT EXISTS assessment_results_user_idx ON assessment_results(user_id, completed_at DESC);
        CREATE TABLE IF NOT EXISTS status_checks (
            id TEXT PRIMARY KEY, client_name TEXT NOT NULL, timestamp TIMESTAMPTZ NOT NULL
        );
        CREATE TABLE IF NOT EXISTS student_profiles (
            user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
            education TEXT NOT NULL, ayush_system TEXT NOT NULL, graduation_year INTEGER NOT NULL,
            interests JSONB NOT NULL, skills JSONB NOT NULL, portfolio_evidence JSONB NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL
        );
        CREATE TABLE IF NOT EXISTS internship_checkins (
            id TEXT PRIMARY KEY, internship_id TEXT NOT NULL REFERENCES internships(id) ON DELETE CASCADE,
            week INTEGER NOT NULL, actor TEXT NOT NULL, meeting_frequency TEXT NOT NULL,
            useful_feedback TEXT NOT NULL, reflection TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL,
            UNIQUE(internship_id, week, actor)
        );
        """
    )


async def seed_demo_data() -> None:
    from lib.demo_data import OPPORTUNITIES, PASSWORD, PROFILE, USERS

    pool = get_pool()
    password_hash = hash_password(PASSWORD)
    for user in USERS:
        await pool.execute(
            """INSERT INTO users (id, email, name, role, institution, readiness, password_hash, updated_at)
               VALUES ($1,$2,$3,$4,$5,$6,$7,NOW())
               ON CONFLICT (id) DO UPDATE SET email=EXCLUDED.email, name=EXCLUDED.name, role=EXCLUDED.role,
               institution=EXCLUDED.institution, readiness=EXCLUDED.readiness, password_hash=EXCLUDED.password_hash,
               updated_at=NOW()""",
            user["id"], user["email"], user["name"], user["role"], user["institution"], user["readiness"], password_hash,
        )
    for opportunity in OPPORTUNITIES:
        await pool.execute(
            """INSERT INTO opportunities (id,type,title,organisation,location,system,mode,stipend,duration,match,skills,gaps,verified,mentor,deliverable,deadline)
               VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16)
               ON CONFLICT (id) DO UPDATE SET type=EXCLUDED.type,title=EXCLUDED.title,organisation=EXCLUDED.organisation,
               location=EXCLUDED.location,system=EXCLUDED.system,mode=EXCLUDED.mode,stipend=EXCLUDED.stipend,
               duration=EXCLUDED.duration,match=EXCLUDED.match,skills=EXCLUDED.skills,gaps=EXCLUDED.gaps,
               verified=EXCLUDED.verified,mentor=EXCLUDED.mentor,deliverable=EXCLUDED.deliverable,deadline=EXCLUDED.deadline""",
            opportunity["id"], opportunity["type"], opportunity["title"], opportunity["organisation"], opportunity["location"],
            opportunity["system"], opportunity["mode"], opportunity["stipend"], opportunity["duration"], opportunity["match"],
            opportunity["skills"], opportunity["gaps"], opportunity["verified"], opportunity["mentor"], opportunity["deliverable"], opportunity["deadline"],
        )
    await pool.execute("UPDATE opportunities SET created_by='demo-employer',publication_status='published' WHERE created_by IS NULL")
    await pool.execute(
        """INSERT INTO student_profiles (user_id,education,ayush_system,graduation_year,interests,skills,portfolio_evidence,updated_at)
           VALUES ($1,$2,$3,$4,$5,$6,$7,NOW()) ON CONFLICT (user_id) DO NOTHING""",
        "demo-student", PROFILE["education"], PROFILE["ayush_system"], PROFILE["graduation_year"],
        PROFILE["interests"], PROFILE["skills"], PROFILE["portfolio_evidence"],
    )
    application_id = await pool.fetchval(
        """INSERT INTO applications (id,user_id,opportunity_id,opportunity_title,organisation,status,next_action,applied_at)
           VALUES ('demo-active-application','demo-student','ayurveda-quality','Ayurveda Quality Associate','Arogya Botanicals','Joined','Complete the Week 4 check-in.',NOW())
           ON CONFLICT (user_id,opportunity_id) DO UPDATE SET status='Joined',next_action='Complete the Week 4 check-in.'
           RETURNING id"""
    )
    await pool.execute(
        """INSERT INTO applications (id,user_id,opportunity_id,opportunity_title,organisation,status,next_action,applied_at)
           VALUES ('demo-blind-application','demo-student','panchakarma-clinic','Panchakarma Clinical Intern','Svastha Ayurveda Centre','Under Review','Employer review in progress.',NOW())
           ON CONFLICT (user_id,opportunity_id) DO UPDATE SET status='Under Review',next_action='Employer review in progress.'"""
    )
    milestones = [
        {"id": "applied", "title": "Application submitted", "detail": "Application accepted.", "status": "complete", "date": "19 Feb"},
        {"id": "mentor", "title": "Mentor assigned", "detail": "Dr. Rahul Mehta", "status": "complete", "date": "20 Feb"},
        {"id": "deliverable", "title": "Deliverable defined", "detail": "QA workflow documentation", "status": "active", "date": "26 Feb"},
        {"id": "evidence", "title": "Evidence pack", "detail": "Generated after final evaluation.", "status": "upcoming", "date": "16 Apr"},
    ]
    internship_id = await pool.fetchval(
        """INSERT INTO internships (id,user_id,application_id,opportunity_title,organisation,week,total_weeks,mentor,deliverable,divergence_alert,milestones)
           VALUES ('demo-active-internship','demo-student',$1,'Ayurveda Quality Associate','Arogya Botanicals',4,8,'Dr. Rahul Mehta','Create a documented QA workflow for one selected production process.',FALSE,$2)
           ON CONFLICT (application_id) DO UPDATE SET week=4,total_weeks=8,mentor=EXCLUDED.mentor,deliverable=EXCLUDED.deliverable,milestones=EXCLUDED.milestones
           RETURNING id""",
        application_id, milestones,
    )
    await pool.execute(
        """INSERT INTO internship_checkins (id,internship_id,week,actor,meeting_frequency,useful_feedback,reflection,created_at)
           VALUES ('demo-mentor-checkin',$1,4,'mentor','Weekly','Yes','Weekly review completed; documentation structure is improving.',$2)
           ON CONFLICT (internship_id,week,actor) DO UPDATE SET meeting_frequency=EXCLUDED.meeting_frequency,useful_feedback=EXCLUDED.useful_feedback,reflection=EXCLUDED.reflection""",
        internship_id, datetime.now(timezone.utc),
    )


async def init_database() -> None:
    await connect_database()
    await init_schema()
    await seed_demo_data()


async def close_database() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def json_value(value: Any) -> Any:
    return value