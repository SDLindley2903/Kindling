"""
Service hours: teens keep a record of what they gave.

Design notes:
- Stewardship first. This is a record of service given, not a resume.
  The wording stays on that side of the line on purpose.
- Hours are self-reported, and the record says so plainly. Honest beats
  impressive.
- Supervisor contact is captured at logging time, while memory is fresh.
  Nothing is worse than needing a phone number for something you did
  two years ago.
- Totals roll up by school year (August through July), because that is
  how schools count.
- Everything is owner-only, same fences as the journal.
"""
import csv
import io
from collections import OrderedDict
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.accounts import require_user
from app.db import ServiceHours, get_engine

router = APIRouter(prefix="/api/serve", tags=["service hours"])

CATEGORIES = ["Church", "School", "Community", "Nonprofit", "Sports", "Other"]


def school_year(d: date) -> str:
    """August starts a new school year. 2026-09-15 -> '2026-27'."""
    start = d.year if d.month >= 8 else d.year - 1
    return f"{start}-{str(start + 1)[-2:]}"


class EntryIn(BaseModel):
    served_on: date
    hours: Decimal = Field(gt=0, le=24)
    organization: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=600)
    category: str = Field(default="Community", max_length=30)
    supervisor_name: str | None = Field(default=None, max_length=80)
    supervisor_email: str | None = Field(default=None, max_length=120)
    supervisor_phone: str | None = Field(default=None, max_length=30)

    @field_validator("category")
    @classmethod
    def known_category(cls, v: str) -> str:
        return v if v in CATEGORIES else "Other"

    @field_validator("served_on")
    @classmethod
    def not_in_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("You cannot log hours for a day that has not happened yet.")
        return v

    @field_validator("hours")
    @classmethod
    def sane_hours(cls, v: Decimal) -> Decimal:
        return Decimal(str(round(float(v), 2)))


def row_out(r: ServiceHours) -> dict:
    return {
        "id": r.id,
        "served_on": r.served_on.isoformat(),
        "hours": float(r.hours),
        "organization": r.organization,
        "description": r.description,
        "category": r.category,
        "supervisor_name": r.supervisor_name or "",
        "supervisor_email": r.supervisor_email or "",
        "supervisor_phone": r.supervisor_phone or "",
        "school_year": school_year(r.served_on),
    }


def load_entries(request: Request):
    with Session(get_engine()) as s:
        user = require_user(request, s)
        rows = s.execute(
            select(ServiceHours)
            .where(ServiceHours.user_id == user.id)
            .order_by(ServiceHours.served_on.desc(), ServiceHours.id.desc())
            .limit(1000)
        ).scalars().all()
        return user.username, [row_out(r) for r in rows]


def summarize(entries: list) -> dict:
    total = round(sum(e["hours"] for e in entries), 2)
    by_cat, by_year, by_org = {}, {}, {}
    for e in entries:
        by_cat[e["category"]] = round(by_cat.get(e["category"], 0) + e["hours"], 2)
        by_year[e["school_year"]] = round(by_year.get(e["school_year"], 0) + e["hours"], 2)
        by_org[e["organization"]] = round(by_org.get(e["organization"], 0) + e["hours"], 2)
    return {
        "total_hours": total,
        "entry_count": len(entries),
        "by_category": OrderedDict(sorted(by_cat.items(), key=lambda x: -x[1])),
        "by_school_year": OrderedDict(sorted(by_year.items(), reverse=True)),
        "by_organization": OrderedDict(sorted(by_org.items(), key=lambda x: -x[1])),
    }


@router.get("")
def list_hours(request: Request):
    _, entries = load_entries(request)
    return {"entries": entries, "summary": summarize(entries), "categories": CATEGORIES}


@router.post("")
def add_hours(entry: EntryIn, request: Request):
    with Session(get_engine()) as s:
        user = require_user(request, s)
        row = ServiceHours(
            user_id=user.id,
            served_on=entry.served_on,
            hours=entry.hours,
            organization=entry.organization.strip(),
            description=entry.description.strip(),
            category=entry.category,
            supervisor_name=(entry.supervisor_name or "").strip() or None,
            supervisor_email=(entry.supervisor_email or "").strip() or None,
            supervisor_phone=(entry.supervisor_phone or "").strip() or None,
        )
        s.add(row)
        s.commit()
        s.refresh(row)
        out = row_out(row)
        from app.grow import record as note_grow
        note_grow(s, user.id, "serve")
    return out


@router.delete("/{entry_id}")
def delete_hours(entry_id: int, request: Request):
    with Session(get_engine()) as s:
        user = require_user(request, s)
        row = s.execute(select(ServiceHours).where(
            ServiceHours.id == entry_id,
            ServiceHours.user_id == user.id)).scalar_one_or_none()
        if not row:
            raise HTTPException(status_code=404, detail="No such entry.")
        s.delete(row)
        s.commit()
    return {"ok": True}


@router.get("/export.csv")
def export_csv(request: Request):
    """A spreadsheet of their record, theirs to share however they need."""
    username, entries = load_entries(request)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Date", "Hours", "Organization", "Category", "What I Did",
                "Supervisor", "Supervisor Email", "Supervisor Phone", "School Year"])
    for e in entries:
        w.writerow([e["served_on"], e["hours"], e["organization"], e["category"],
                    e["description"], e["supervisor_name"], e["supervisor_email"],
                    e["supervisor_phone"], e["school_year"]])
    summary = summarize(entries)
    w.writerow([])
    w.writerow(["TOTAL HOURS", summary["total_hours"]])
    w.writerow(["Entries", summary["entry_count"]])
    w.writerow([])
    w.writerow(["Hours by school year"])
    for year, hrs in summary["by_school_year"].items():
        w.writerow([year, hrs])
    w.writerow([])
    w.writerow(["Hours by category"])
    for cat, hrs in summary["by_category"].items():
        w.writerow([cat, hrs])
    w.writerow([])
    w.writerow(["Hours are self-reported. Supervisor contacts are listed so any entry can be confirmed."])
    buf.seek(0)
    filename = f"service-hours-{username}-{date.today().isoformat()}.csv"
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
