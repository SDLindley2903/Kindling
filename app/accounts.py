"""
The accounts station: sign up, sign in, favorites, journal, streaks.

Privacy stance, in plain words: we ask for a username and a password.
That is all. No email, no real name, no birthday. The less we know
about a teenager, the less anyone could ever misuse.

Security choices (the level 5 gate):
- Passwords are hashed with bcrypt. We could not read them if we tried.
- Sessions are random tokens stored server side, in a cookie the page's
  JavaScript cannot touch (httponly), sent only to our site (samesite).
- Login gets throttled after repeated failures. Guessing gets boring fast.
- Every input is validated for shape and length before it touches anything.
- All database access goes through the ORM: no hand-built SQL, no injection.
"""
import re
import secrets
import time
from datetime import date, timedelta

import bcrypt
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db import (Activity, Favorite, JournalEntry, SessionToken, User,
                    get_engine, utcnow)

router = APIRouter(prefix="/api", tags=["accounts"])

COOKIE = "kindling_session"
SESSION_DAYS = 30
USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")

# Failed-login memory: username -> recent failure timestamps
_failed: dict = {}
FAIL_LIMIT = 5
FAIL_WINDOW = 300   # look at the last 5 minutes
LOCK_SECONDS = 60   # cool off for a minute


# ---------------------------------------------------------------- helpers

def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("ascii")


def check_password(pw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(pw.encode("utf-8"), hashed.encode("ascii"))
    except ValueError:
        return False


def throttled(username: str) -> bool:
    now = time.time()
    arr = [t for t in _failed.get(username, []) if now - t < FAIL_WINDOW]
    _failed[username] = arr
    return len(arr) >= FAIL_LIMIT and (now - arr[-1]) < LOCK_SECONDS


def note_failure(username: str):
    _failed.setdefault(username, []).append(time.time())


def set_session_cookie(resp: Response, request: Request, token: str):
    https = request.headers.get("x-forwarded-proto", request.url.scheme) == "https"
    resp.set_cookie(COOKIE, token, max_age=SESSION_DAYS * 86400,
                    httponly=True, samesite="lax", secure=https, path="/")


def user_from_request(request: Request, s: Session):
    token = request.cookies.get(COOKIE)
    if not token or len(token) > 64:
        return None
    row = s.execute(select(SessionToken).where(SessionToken.token == token)).scalar_one_or_none()
    if not row or row.expires_at < utcnow():
        return None
    return s.get(User, row.user_id)


def require_user(request: Request, s: Session) -> User:
    user = user_from_request(request, s)
    if not user:
        raise HTTPException(status_code=401, detail="Please sign in first.")
    return user


def start_session(s: Session, user: User) -> str:
    token = secrets.token_urlsafe(32)[:64]
    s.add(SessionToken(token=token, user_id=user.id,
                       expires_at=utcnow() + timedelta(days=SESSION_DAYS)))
    s.commit()
    return token


def record_today_and_streak(s: Session, user: User) -> int:
    today = date.today()
    seen = s.execute(select(Activity.day).where(
        Activity.user_id == user.id,
        Activity.day >= today - timedelta(days=400))).scalars().all()
    days = set(seen)
    if today not in days:
        s.add(Activity(user_id=user.id, day=today))
        s.commit()
        days.add(today)
    streak, d = 0, today
    while d in days:
        streak += 1
        d = d - timedelta(days=1)
    return streak


# ---------------------------------------------------------------- shapes

class Credentials(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=8, max_length=72)

    @field_validator("username")
    @classmethod
    def username_shape(cls, v: str) -> str:
        if not USERNAME_RE.match(v):
            raise ValueError("Usernames are 3 to 20 letters, numbers, or underscores.")
        return v.lower()


class FavoriteIn(BaseModel):
    ref: str = Field(min_length=3, max_length=40)
    text: str = Field(min_length=1, max_length=1500)
    translation: str = Field(default="BSB", max_length=8)
    topic_id: str | None = Field(default=None, max_length=20)


class JournalIn(BaseModel):
    body: str = Field(min_length=1, max_length=4000)


# ---------------------------------------------------------------- account

@router.post("/signup")
def signup(creds: Credentials, request: Request, response: Response):
    with Session(get_engine()) as s:
        exists = s.execute(select(User).where(User.username == creds.username)).scalar_one_or_none()
        if exists:
            raise HTTPException(status_code=409, detail="That name is taken. Pick another.")
        user = User(username=creds.username, password_hash=hash_password(creds.password))
        s.add(user)
        s.commit()
        s.refresh(user)
        token = start_session(s, user)
        streak = record_today_and_streak(s, user)
        username_out = user.username
    set_session_cookie(response, request, token)
    return {"username": username_out, "streak": streak}


@router.post("/login")
def login(creds: Credentials, request: Request, response: Response):
    if throttled(creds.username):
        raise HTTPException(status_code=429,
                            detail="Too many tries. Take a breath and try again in a minute.")
    with Session(get_engine()) as s:
        user = s.execute(select(User).where(User.username == creds.username)).scalar_one_or_none()
        if not user or not check_password(creds.password, user.password_hash):
            note_failure(creds.username)
            raise HTTPException(status_code=401, detail="Wrong username or password.")
        token = start_session(s, user)
        streak = record_today_and_streak(s, user)
        username_out = user.username
    set_session_cookie(response, request, token)
    return {"username": username_out, "streak": streak}


@router.post("/logout")
def logout(request: Request, response: Response):
    token = request.cookies.get(COOKIE)
    if token:
        with Session(get_engine()) as s:
            s.execute(delete(SessionToken).where(SessionToken.token == token))
            s.commit()
    response.delete_cookie(COOKIE, path="/")
    return {"ok": True}


@router.get("/me")
def me(request: Request):
    with Session(get_engine()) as s:
        user = require_user(request, s)
        streak = record_today_and_streak(s, user)
        username_out = user.username
        favs = s.execute(select(Favorite).where(Favorite.user_id == user.id)
                         .order_by(Favorite.id.desc())).scalars().all()
        fav_out = [{"ref": f.ref, "text": f.text, "translation": f.translation,
                    "topic_id": f.topic_id} for f in favs]
    return {"username": username_out, "streak": streak, "favorites": fav_out}


# ---------------------------------------------------------------- favorites

@router.post("/favorites")
def toggle_favorite(fav: FavoriteIn, request: Request):
    with Session(get_engine()) as s:
        user = require_user(request, s)
        existing = s.execute(select(Favorite).where(
            Favorite.user_id == user.id, Favorite.ref == fav.ref)).scalar_one_or_none()
        if existing:
            s.delete(existing)
            s.commit()
            return {"ref": fav.ref, "saved": False}
        s.add(Favorite(user_id=user.id, ref=fav.ref, text=fav.text,
                       translation=fav.translation, topic_id=fav.topic_id))
        s.commit()
    return {"ref": fav.ref, "saved": True}


@router.get("/favorites")
def list_favorites(request: Request):
    with Session(get_engine()) as s:
        user = require_user(request, s)
        favs = s.execute(select(Favorite).where(Favorite.user_id == user.id)
                         .order_by(Favorite.id.desc()).limit(500)).scalars().all()
        fav_out = [{"ref": f.ref, "text": f.text, "translation": f.translation,
                    "topic_id": f.topic_id} for f in favs]
    return {"favorites": fav_out}


# ---------------------------------------------------------------- journal

@router.post("/journal")
def add_journal(entry: JournalIn, request: Request):
    with Session(get_engine()) as s:
        user = require_user(request, s)
        row = JournalEntry(user_id=user.id, body=entry.body)
        s.add(row)
        s.commit()
        s.refresh(row)
        out = {"id": row.id, "body": row.body, "created_at": row.created_at.isoformat()}
        from app.grow import record as note_grow
        note_grow(s, user.id, "journal")
    return out


@router.get("/journal")
def list_journal(request: Request):
    with Session(get_engine()) as s:
        user = require_user(request, s)
        rows = s.execute(select(JournalEntry).where(JournalEntry.user_id == user.id)
                         .order_by(JournalEntry.id.desc()).limit(200)).scalars().all()
        out = [{"id": r.id, "body": r.body,
                "created_at": r.created_at.isoformat()} for r in rows]
    return {"entries": out}


@router.delete("/journal/{entry_id}")
def delete_journal(entry_id: int, request: Request):
    with Session(get_engine()) as s:
        user = require_user(request, s)
        row = s.execute(select(JournalEntry).where(
            JournalEntry.id == entry_id,
            JournalEntry.user_id == user.id)).scalar_one_or_none()
        if not row:
            raise HTTPException(status_code=404, detail="No such entry.")
        s.delete(row)
        s.commit()
    return {"ok": True}
