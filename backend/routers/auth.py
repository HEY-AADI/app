import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from lib.db import get_pool
from lib.security import verify_password
from models.auth import LoginRequest, SessionResponse, UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])
SESSION_COOKIE = "samanvaya_session"
SESSION_DAYS = 7


def _user_public(document: dict) -> UserPublic:
    return UserPublic(
        id=document["id"],
        email=document["email"],
        name=document["name"],
        role=document["role"],
        institution=document.get("institution"),
        readiness=document.get("readiness", 0),
    )


async def get_current_user(request: Request) -> dict:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    session_row = await get_pool().fetchrow("SELECT token,user_id,expires_at FROM sessions WHERE token=$1", token)
    session = dict(session_row) if session_row else None
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
    expires_at = session["expires_at"].replace(tzinfo=timezone.utc) if session["expires_at"].tzinfo is None else session["expires_at"]
    if expires_at <= datetime.now(timezone.utc):
        await get_pool().execute("DELETE FROM sessions WHERE token=$1", token)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
    user_row = await get_pool().fetchrow("SELECT id,email,name,role,institution,readiness,password_hash FROM users WHERE id=$1", session["user_id"])
    user = dict(user_row) if user_row else None
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account not found")
    return user


@router.post("/login", response_model=SessionResponse)
async def login(payload: LoginRequest, response: Response):
    user_row = await get_pool().fetchrow("SELECT id,email,name,role,institution,readiness,password_hash FROM users WHERE email=$1", payload.email.lower().strip())
    user = dict(user_row) if user_row else None
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password is incorrect")
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    await get_pool().execute("INSERT INTO sessions (token,user_id,created_at,expires_at) VALUES ($1,$2,$3,$4)", token, user["id"], now, now + timedelta(days=SESSION_DAYS))
    response.set_cookie(SESSION_COOKIE, token, max_age=SESSION_DAYS * 86400, httponly=True, samesite="lax", secure=False, path="/")
    return SessionResponse(user=_user_public(user))


@router.get("/me", response_model=UserPublic)
async def me(user: dict = Depends(get_current_user)):
    return _user_public(user)


@router.post("/logout", status_code=204)
async def logout(request: Request, response: Response):
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        await get_pool().execute("DELETE FROM sessions WHERE token=$1", token)
    response.delete_cookie(SESSION_COOKIE, path="/")