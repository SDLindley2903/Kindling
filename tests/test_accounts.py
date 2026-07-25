"""
Account and security tests (levels 2-3 plus the level 5 security gate).
Every door gets rattled: wrong passwords, injection strings, other
people's journals, brute force. The locks should hold.
"""
import os
import secrets
import sys

from fastapi.testclient import TestClient

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from app.db import Base, get_engine  # noqa: E402
from app.main import app  # noqa: E402

Base.metadata.create_all(get_engine())


def fresh():
    """A brand-new browser with no cookies."""
    return TestClient(app)


def name():
    return "tester_" + secrets.token_hex(4)


PW = "sunrise-strong-99"


def signup(c, username=None, pw=PW):
    return c.post("/api/signup", json={"username": username or name(), "password": pw})


# ---------------------------------------------------------------- accounts

def test_signup_me_and_streak():
    c = fresh()
    u = name()
    r = signup(c, u)
    assert r.status_code == 200
    assert r.json()["username"] == u
    me = c.get("/api/me")
    assert me.status_code == 200
    assert me.json()["username"] == u
    assert me.json()["streak"] >= 1, "day one lights the flame"


def test_duplicate_username_blocked():
    c = fresh()
    u = name()
    assert signup(c, u).status_code == 200
    assert signup(fresh(), u).status_code == 409


def test_login_and_logout():
    c = fresh()
    u = name()
    signup(c, u)
    c2 = fresh()
    assert c2.post("/api/login", json={"username": u, "password": "wrong-password-1"}).status_code == 401
    ok = c2.post("/api/login", json={"username": u, "password": PW})
    assert ok.status_code == 200
    assert c2.get("/api/me").status_code == 200
    c2.post("/api/logout")
    assert c2.get("/api/me").status_code == 401, "logout really closes the door"


# ---------------------------------------------------------------- security gate

def test_input_validation():
    c = fresh()
    # SQL injection shaped username: rejected by shape rules before touching anything
    r = c.post("/api/signup", json={"username": "a'; DROP TABLE users;--", "password": PW})
    assert r.status_code == 422
    # short password
    assert c.post("/api/signup", json={"username": name(), "password": "short"}).status_code == 422
    # absurdly long username
    assert c.post("/api/signup", json={"username": "x" * 500, "password": PW}).status_code == 422


def test_brute_force_throttle():
    c = fresh()
    u = name()
    signup(c, u)
    attacker = fresh()
    for _ in range(5):
        attacker.post("/api/login", json={"username": u, "password": "guess-wrong-99"})
    blocked = attacker.post("/api/login", json={"username": u, "password": PW})
    assert blocked.status_code == 429, "after 5 misses, even the right key waits a minute"


def test_session_cookie_flags():
    c = fresh()
    r = signup(c)
    cookie = r.headers.get("set-cookie", "")
    assert "httponly" in cookie.lower(), "page scripts cannot read the session"
    assert "samesite=lax" in cookie.lower(), "the cookie stays home"


def test_passwords_are_hashed():
    from sqlalchemy import select
    from sqlalchemy.orm import Session
    from app.db import User
    c = fresh()
    u = name()
    signup(c, u)
    with Session(get_engine()) as s:
        row = s.execute(select(User).where(User.username == u)).scalar_one()
    assert PW not in row.password_hash, "never store the real password"
    assert row.password_hash.startswith("$2"), "bcrypt fingerprint"


def test_auth_required_everywhere_private():
    nobody = fresh()
    assert nobody.get("/api/me").status_code == 401
    assert nobody.get("/api/journal").status_code == 401
    assert nobody.get("/api/favorites").status_code == 401
    assert nobody.post("/api/journal", json={"body": "hi"}).status_code == 401
    assert nobody.post("/api/favorites",
                       json={"ref": "John 3:16", "text": "x"}).status_code == 401


# ---------------------------------------------------------------- favorites

def test_favorites_toggle():
    c = fresh()
    signup(c)
    fav = {"ref": "John 3:16", "text": "For God so loved the world...",
           "translation": "BSB", "topic_id": None}
    assert c.post("/api/favorites", json=fav).json()["saved"] is True
    assert len(c.get("/api/favorites").json()["favorites"]) == 1
    assert c.post("/api/favorites", json=fav).json()["saved"] is False, "second tap unhearts"
    assert len(c.get("/api/favorites").json()["favorites"]) == 0


# ---------------------------------------------------------------- journal

def test_journal_private_and_owned():
    c1, c2 = fresh(), fresh()
    signup(c1)
    signup(c2)
    made = c1.post("/api/journal", json={"body": "God met me today."})
    assert made.status_code == 200
    entry_id = made.json()["id"]
    assert len(c1.get("/api/journal").json()["entries"]) == 1
    assert len(c2.get("/api/journal").json()["entries"]) == 0, "journals never leak"
    assert c2.delete(f"/api/journal/{entry_id}").status_code == 404, "cannot delete someone else's words"
    assert c1.delete(f"/api/journal/{entry_id}").status_code == 200
    assert len(c1.get("/api/journal").json()["entries"]) == 0


def test_journal_limits_and_xss_storage():
    c = fresh()
    signup(c)
    assert c.post("/api/journal", json={"body": "x" * 4001}).status_code == 422, "4000 char cap"
    sneaky = "<script>alert('hi')</script> God is good"
    r = c.post("/api/journal", json={"body": sneaky})
    assert r.status_code == 200
    assert r.json()["body"] == sneaky, ("stored as plain data; the page escapes all text "
                                        "when showing it, so it can never run")
