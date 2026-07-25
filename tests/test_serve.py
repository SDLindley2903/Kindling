"""
Service hours tests: the math has to be right, because a college or
scholarship application is not the place to find out it was not.
"""
import os
import secrets
import sys
from datetime import date, timedelta

from fastapi.testclient import TestClient

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from app.db import Base, get_engine  # noqa: E402
from app.main import app  # noqa: E402
from app.serve import school_year  # noqa: E402

Base.metadata.create_all(get_engine())
PW = "sunrise-strong-99"


def signed_client():
    c = TestClient(app)
    c.post("/api/signup", json={"username": "serv_" + secrets.token_hex(4), "password": PW})
    return c


def entry(day="2026-03-14", hours=2.5, org="First Baptist Youth", **kw):
    body = {"served_on": day, "hours": hours, "organization": org,
            "description": "Served meals at the food pantry.", "category": "Church"}
    body.update(kw)
    return body


# ---------------------------------------------------------------- basics

def test_log_and_list():
    c = signed_client()
    r = c.post("/api/serve", json=entry())
    assert r.status_code == 200
    assert r.json()["hours"] == 2.5
    d = c.get("/api/serve").json()
    assert len(d["entries"]) == 1
    assert d["summary"]["total_hours"] == 2.5


def test_totals_add_up():
    c = signed_client()
    c.post("/api/serve", json=entry(day="2026-03-14", hours=2.5, category="Church"))
    c.post("/api/serve", json=entry(day="2026-04-02", hours=4, org="Habitat", category="Community"))
    c.post("/api/serve", json=entry(day="2025-10-05", hours=3.25, org="Food Bank", category="Nonprofit"))
    sm = c.get("/api/serve").json()["summary"]
    assert sm["total_hours"] == 9.75
    assert sm["entry_count"] == 3
    assert sm["by_category"]["Church"] == 2.5
    assert sm["by_category"]["Community"] == 4
    assert sm["by_school_year"]["2025-26"] == 9.75, "Oct 2025 through Apr 2026 is one school year"


def test_school_year_boundary():
    """August starts the new school year, the way schools count it."""
    assert school_year(date(2026, 7, 31)) == "2025-26"
    assert school_year(date(2026, 8, 1)) == "2026-27"
    assert school_year(date(2026, 12, 25)) == "2026-27"
    assert school_year(date(2027, 5, 1)) == "2026-27"


def test_supervisor_info_saved():
    c = signed_client()
    r = c.post("/api/serve", json=entry(
        supervisor_name="Pastor Mike", supervisor_email="mike@church.org",
        supervisor_phone="555-123-4567"))
    d = r.json()
    assert d["supervisor_name"] == "Pastor Mike"
    assert d["supervisor_email"] == "mike@church.org"
    assert d["supervisor_phone"] == "555-123-4567"


# ---------------------------------------------------------------- guardrails

def test_no_future_hours():
    c = signed_client()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    assert c.post("/api/serve", json=entry(day=tomorrow)).status_code == 422


def test_hour_limits():
    c = signed_client()
    assert c.post("/api/serve", json=entry(hours=0)).status_code == 422
    assert c.post("/api/serve", json=entry(hours=25)).status_code == 422
    assert c.post("/api/serve", json=entry(hours=-3)).status_code == 422


def test_required_fields():
    c = signed_client()
    assert c.post("/api/serve", json=entry(organization="")).status_code == 422
    assert c.post("/api/serve", json=entry(description="")).status_code == 422
    assert c.post("/api/serve", json=entry(description="x" * 601)).status_code == 422


def test_unknown_category_becomes_other():
    c = signed_client()
    r = c.post("/api/serve", json=entry(category="Hackerville"))
    assert r.json()["category"] == "Other"


# ---------------------------------------------------------------- privacy

def test_hours_are_private():
    c1, c2 = signed_client(), signed_client()
    made = c1.post("/api/serve", json=entry()).json()
    assert len(c1.get("/api/serve").json()["entries"]) == 1
    assert len(c2.get("/api/serve").json()["entries"]) == 0, "hours never leak between students"
    assert c2.delete(f"/api/serve/{made['id']}").status_code == 404
    assert c1.delete(f"/api/serve/{made['id']}").status_code == 200
    assert len(c1.get("/api/serve").json()["entries"]) == 0


def test_signin_required():
    nobody = TestClient(app)
    assert nobody.get("/api/serve").status_code == 401
    assert nobody.post("/api/serve", json=entry()).status_code == 401
    assert nobody.get("/api/serve/export.csv").status_code == 401


# ---------------------------------------------------------------- export

def test_csv_export():
    c = signed_client()
    c.post("/api/serve", json=entry(hours=2.5, supervisor_name="Pastor Mike"))
    c.post("/api/serve", json=entry(day="2026-04-02", hours=4, org="Habitat"))
    r = c.get("/api/serve/export.csv")
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
    assert "attachment" in r.headers["content-disposition"]
    body = r.text
    assert "Supervisor Email" in body
    assert "Pastor Mike" in body
    assert "Habitat" in body
    assert "TOTAL HOURS" in body and "6.5" in body
    assert "self-reported" in body


def test_serve_flag_on():
    c = TestClient(app)
    assert c.get("/api/topics").json()["serve_enabled"] is True
