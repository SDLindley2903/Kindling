"""
Grow: the daily rhythm tracker.

The heart of it: walking with God is a daily thing, and small faithful days
stack into something real. This shows a teen that stacking.

Two ways a day fills up:
- Automatic. Open a card, read a chapter, write in the journal, log service
  hours. The app notices. Nothing to remember, nothing to fake.
- Checked. Prayer and encouraging someone are between them and God, so
  those they mark themselves.

A guardrail on the heart: this is a mirror, not a scoreboard. Missing a day
is not failure, and the app says so out loud. Grace over guilt, every time.
"""
from datetime import date, timedelta

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.accounts import require_user
from app.db import DailyAction, get_engine

router = APIRouter(prefix="/api/grow", tags=["grow"])

# What the app notices on its own
AUTO_ACTIONS = {
    "card": "Opened a card",
    "scripture": "Read Scripture",
    "journal": "Wrote in the journal",
    "serve": "Logged service",
}

# What the teen marks themselves
CHECK_ACTIONS = {
    "prayer": "Prayed",
    "encouraged": "Encouraged someone",
}

ALL_ACTIONS = {**AUTO_ACTIONS, **CHECK_ACTIONS}
HEATMAP_WEEKS = 12


class ActionIn(BaseModel):
    action: str = Field(min_length=1, max_length=20)

    @field_validator("action")
    @classmethod
    def known(cls, v: str) -> str:
        if v not in ALL_ACTIONS:
            raise ValueError("Not something Kindling tracks.")
        return v


def record(s: Session, user_id: int, action: str, source: str = "auto") -> None:
    """
    Mark one thing done today. Safe to call over and over: the database
    keeps one row per person, per day, per action.
    """
    if action not in ALL_ACTIONS:
        return
    today = date.today()
    exists = s.execute(select(DailyAction.id).where(
        DailyAction.user_id == user_id,
        DailyAction.day == today,
        DailyAction.action == action)).scalar_one_or_none()
    if exists:
        return
    s.add(DailyAction(user_id=user_id, day=today, action=action, source=source))
    s.commit()


def days_map(s: Session, user_id: int, since: date) -> dict:
    """-> {date: set(actions)} for everything since a given day."""
    rows = s.execute(select(DailyAction.day, DailyAction.action).where(
        DailyAction.user_id == user_id,
        DailyAction.day >= since)).all()
    out = {}
    for day, action in rows:
        out.setdefault(day, set()).add(action)
    return out


def streaks(active_days: set, today: date) -> dict:
    """
    Current streak counts back from today. A day still in progress does not
    break it: if nothing is logged today yet, we start counting at yesterday,
    because the day is not over and grace is not stingy.
    """
    current = 0
    cursor = today if today in active_days else today - timedelta(days=1)
    while cursor in active_days:
        current += 1
        cursor -= timedelta(days=1)

    best = 0
    if active_days:
        run = 0
        prev = None
        for d in sorted(active_days):
            run = run + 1 if (prev and (d - prev).days == 1) else 1
            best = max(best, run)
            prev = d
    return {"current": current, "best": max(best, current)}


@router.get("")
def overview(request: Request):
    with Session(get_engine()) as s:
        user = require_user(request, s)
        today = date.today()
        # Monday-start grid, HEATMAP_WEEKS worth
        end = today + timedelta(days=(6 - today.weekday()))
        start = end - timedelta(weeks=HEATMAP_WEEKS) + timedelta(days=1)
        recent = days_map(s, user.id, start)

        all_rows = s.execute(select(DailyAction.day).where(
            DailyAction.user_id == user.id)).scalars().all()
        active_days = set(all_rows)

        grid = []
        d = start
        while d <= end:
            acts = recent.get(d, set())
            grid.append({
                "day": d.isoformat(),
                "count": len(acts),
                "future": d > today,
                "today": d == today,
            })
            d += timedelta(days=1)

        todays = sorted(recent.get(today, set()))
        week_start = today - timedelta(days=today.weekday())
        this_week = sum(1 for x in active_days if week_start <= x <= today)

        st = streaks(active_days, today)
    return {
        "streak": st["current"],
        "best_streak": st["best"],
        "days_total": len(active_days),
        "this_week": this_week,
        "today": today.isoformat(),
        "today_actions": todays,
        "grid": grid,
        "auto_actions": AUTO_ACTIONS,
        "check_actions": CHECK_ACTIONS,
    }


@router.post("/check")
def toggle_check(body: ActionIn, request: Request):
    """Teen marks (or unmarks) something only they can know they did."""
    if body.action not in CHECK_ACTIONS:
        raise HTTPException(status_code=422,
                            detail="Kindling notices that one on its own.")
    with Session(get_engine()) as s:
        user = require_user(request, s)
        today = date.today()
        existing = s.execute(select(DailyAction).where(
            DailyAction.user_id == user.id,
            DailyAction.day == today,
            DailyAction.action == body.action)).scalar_one_or_none()
        if existing:
            s.execute(delete(DailyAction).where(DailyAction.id == existing.id))
            s.commit()
            return {"action": body.action, "done": False}
        s.add(DailyAction(user_id=user.id, day=today,
                          action=body.action, source="checked"))
        s.commit()
    return {"action": body.action, "done": True}


@router.post("/note")
def note_action(body: ActionIn, request: Request):
    """
    The app quietly noticing something. Called by the page when a teen
    opens a card or reads a chapter. Signed-out visitors are ignored
    silently, because tracking should never block reading God's Word.
    """
    with Session(get_engine()) as s:
        user = require_user(request, s)
        if body.action not in AUTO_ACTIONS:
            raise HTTPException(status_code=422, detail="Not an automatic action.")
        record(s, user.id, body.action, "auto")
    return {"ok": True}
