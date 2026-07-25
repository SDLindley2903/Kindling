"""
Level 1 smoke tests for Kindling (light and fast, like flipping the lights on).
Run with:  pytest tests/ -v
"""
import json
import os
import re
import sys

import pytest
from fastapi.testclient import TestClient

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from app.main import app  # noqa: E402

client = TestClient(app)
TRANSLATIONS = ["BSB", "WEB", "KJV"]


# ---------- does the stand open? ----------

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_homepage_loads():
    r = client.get("/")
    assert r.status_code == 200
    html = r.text
    assert "Kindling" in html
    assert 'id="grid"' in html          # card grid is there
    assert 'id="votd"' in html          # verse of the day is there
    assert 'id="pills"' in html         # translation switch is there
    assert "988" in html                # care line in the footer


# ---------- is the food real? ----------

def test_topics_menu():
    r = client.get("/api/topics")
    assert r.status_code == 200
    data = r.json()
    assert data["app"] == "Kindling"
    assert len(data["topics"]) == 12
    ids = [t["id"] for t in data["topics"]]
    assert ids[0] == "identity", "Identity leads the deck"
    for newcomer in ("forgiveness", "selfworth", "family", "temptation"):
        assert newcomer in ids
    for t in data["topics"]:
        assert len(t["verses"]) >= 6, t["id"]
        assert len(t["questions"]) == 3, t["id"]
        assert t["intro"] and t["meaning"] and t["next_step"], t["id"]
        for v in t["verses"]:
            for tr in TRANSLATIONS:
                assert v.get(tr, "").strip(), f"{t['id']} {v['ref']} missing {tr}"
            assert re.match(r"^[1-3]?\s?[A-Za-z ]+ \d+:\d+(-\d+)?$", v["ref"]), v["ref"]


def test_single_topic_and_404():
    r = client.get("/api/topics/identity")
    assert r.status_code == 200
    assert r.json()["title"] == "Identity"
    assert client.get("/api/topics/nope").status_code == 404


def test_heavy_cards_carry_care_note():
    data = client.get("/api/topics").json()
    for t in data["topics"]:
        if t["heavy"]:
            assert "988" in t.get("care_note", ""), f"{t['id']} needs the care note"


def test_phase4_ui_present():
    html = client.get("/").text
    assert 'id="view-lesson"' in html, "leader lesson view exists"
    assert 'id="view-ask"' in html, "ask view exists"
    assert "shareVerse" in html, "share cards wired in"
    assert 'data-need="ask"' in html, "ask tab gated by server flag"


def test_verse_of_the_day():
    r = client.get("/api/votd")
    assert r.status_code == 200
    v = r.json()
    assert v["ref"] and v["BSB"].strip()


# ---------- exact words, spot-checked against known Scripture ----------

def test_scripture_spot_checks():
    data = client.get("/api/topics").json()
    flat = {(t["id"], v["ref"]): v for t in data["topics"] for v in t["verses"]}
    assert "fearfully and wonderfully made" in flat[("identity", "Psalm 139:14")]["BSB"]
    assert "Cast all your anxiety on Him" in flat[("anxiety", "1 Peter 5:7")]["BSB"]
    assert "near to the brokenhearted" in flat[("depression", "Psalm 34:18")]["BSB"]
    assert "I will never leave thee" in flat[("loneliness", "Hebrews 13:5")]["KJV"]


# ---------- takeout box ----------

def test_standalone_file():
    path = os.path.join(os.path.dirname(ROOT), "Kindling.html")
    assert os.path.exists(path), "Run scripts/make_standalone.py first"
    with open(path, encoding="utf-8") as f:
        html = f.read()
    assert "window.KINDLING_DATA" in html
    payload = re.search(r"window\.KINDLING_DATA = (\{.*?\});</script>", html, re.S)
    assert payload, "embedded data should be readable"
    data = json.loads(payload.group(1))
    assert len(data["topics"]) == 12
    assert not data.get("bible_enabled"), "takeout box hides Read/Search tabs"
