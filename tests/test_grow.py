"""
Grow tests. Streak math has to be exactly right, because a teen who
walked 12 days straight should never be told they walked 11.
"""
import os
import secrets
import sys
from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from app.db import Base, DailyAction, User, get_engine  # noqa: E402
from app.grow import streaks  # noqa: E402
from app.main import app  # noqa: E402
from sqlalchemy import select  # noqa: E402

Base.metadata.create_all(get_engine())
PW = "sunrise-strong-99"


def signed_client():
    c = TestClient(app)
    name = "grow_" + secrets.token_hex(4)
    c.post("/api/signup", json={"username": name, "password": PW})
    return c, name


def user_id_for(name):
    with Session(get_engine()) as s:
        return s.execute(select(User.id).where(User.username == name)).scalar_one()


def seed_days(uid, days_ago_list, action="card"):
    """Plant history directly, so we can test streaks across real calendars."""
    with Session(get_engine()) as s:
        for n in days_ago_list:
            s.add(DailyAction(user_id=uid, day=date.today() - timedelta(days=n),
                              action=action, source="auto"))
        s.commit()


# ---------------------------------------------------------------- streak math

def test_streak_counts_back_from_today():
    today = date.today()
    days = {today, today - timedelta(days=1), today - timedelta(days=2)}
    assert streaks(days, today)["current"] == 3


def test_yesterday_streak_survives_an_unstarted_today():
    """The day is not over yet. Grace is not stingy."""
    today = date.today()
    days = {today - timedelta(days=1), today - timedelta(days=2)}
    assert streaks(days, today)["current"] == 2, "today has not happened yet, streak holds"


def test_gap_breaks_the_streak():
    today = date.today()
    days = {today, today - timedelta(days=3), today - timedelta(days=4)}
    st = streaks(days, today)
    assert st["current"] == 1
    assert st["best"] == 2, "the old two-day run is still their best"


def test_best_streak_remembered():
    today = date.today()
    days = {today - timedelta(days=n) for n in (0, 1, 10, 11, 12, 13, 14)}
    st = streaks(days, today)
    assert st["current"] == 2
    assert st["best"] == 5


def test_empty_history():
    st = streaks(set(), date.today())
    assert st["current"] == 0 and st["best"] == 0


# ---------------------------------------------------------------- the API

def test_overview_starts_empty():
    c, _ = signed_client()
    d = c.get("/api/grow").json()
    assert d["streak"] == 0
    assert d["days_total"] == 0
    assert len(d["grid"]) == 12 * 7, "12 full weeks of squares"
    assert "prayer" in d["check_actions"]
    assert "card" in d["auto_actions"]


def test_note_action_counts_today():
    c, _ = signed_client()
    assert c.post("/api/grow/note", json={"action": "card"}).status_code == 200
    d = c.get("/api/grow").json()
    assert d["streak"] == 1
    assert "card" in d["today_actions"]


def test_note_is_safe_to_repeat():
    c, _ = signed_client()
    for _ in range(4):
        c.post("/api/grow/note", json={"action": "scripture"})
    d = c.get("/api/grow").json()
    assert d["today_actions"] == ["scripture"], "one row per day per action, no double counting"
    assert d["days_total"] == 1


def test_check_toggles_on_and_off():
    c, _ = signed_client()
    assert c.post("/api/grow/check", json={"action": "prayer"}).json()["done"] is True
    assert "prayer" in c.get("/api/grow").json()["today_actions"]
    assert c.post("/api/grow/check", json={"action": "prayer"}).json()["done"] is False
    assert "prayer" not in c.get("/api/grow").json()["today_actions"]


def test_cannot_check_an_automatic_action():
    c, _ = signed_client()
    r = c.post("/api/grow/check", json={"action": "card"})
    assert r.status_code == 422, "reading a card cannot be clicked into existence"


def test_unknown_actions_rejected():
    c, _ = signed_client()
    assert c.post("/api/grow/note", json={"action": "flossing"}).status_code == 422
    assert c.post("/api/grow/check", json={"action": "x" * 50}).status_code == 422


def test_heatmap_counts_stack():
    c, _ = signed_client()
    for a in ("card", "scripture"):
        c.post("/api/grow/note", json={"action": a})
    c.post("/api/grow/check", json={"action": "prayer"})
    d = c.get("/api/grow").json()
    today_cell = [g for g in d["grid"] if g["today"]][0]
    assert today_cell["count"] == 3, "three different things today makes a brighter square"


def test_real_streak_over_seeded_history():
    c, name = signed_client()
    uid = user_id_for(name)
    seed_days(uid, [1, 2, 3, 4], action="scripture")
    c.post("/api/grow/note", json={"action": "card"})
    d = c.get("/api/grow").json()
    assert d["streak"] == 5, "four seeded days plus today"
    assert d["days_total"] == 5


# ---------------------------------------------------------------- privacy

def test_grow_is_private():
    c1, _ = signed_client()
    c2, _ = signed_client()
    c1.post("/api/grow/note", json={"action": "card"})
    assert c1.get("/api/grow").json()["days_total"] == 1
    assert c2.get("/api/grow").json()["days_total"] == 0, "days never leak between teens"


def test_signin_required():
    nobody = TestClient(app)
    assert nobody.get("/api/grow").status_code == 401
    assert nobody.post("/api/grow/note", json={"action": "card"}).status_code == 401
    assert nobody.post("/api/grow/check", json={"action": "prayer"}).status_code == 401


# ---------------------------------------------------------------- automatic wiring

def test_journal_and_serve_count_automatically():
    c, _ = signed_client()
    c.post("/api/journal", json={"body": "God met me today."})
    c.post("/api/serve", json={"served_on": date.today().isoformat(), "hours": 2,
                               "organization": "Food Bank",
                               "description": "Sorted donations.", "category": "Community"})
    acts = c.get("/api/grow").json()["today_actions"]
    assert "journal" in acts, "writing in the journal counts on its own"
    assert "serve" in acts, "logging service counts on its own"


def test_grow_flag_on():
    c = TestClient(app)
    assert c.get("/api/topics").json()["grow_enabled"] is True
