"""
Ask Kindling tests, level 2 style: the AI is mocked (a pretend Claude),
so these run instantly, cost nothing, and prove all the fences hold.
"""
import os
import secrets
import sys

from fastapi.testclient import TestClient

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import app.ask as ask_mod  # noqa: E402
from app.main import app  # noqa: E402

PW = "sunrise-strong-99"


def signed_client():
    c = TestClient(app)
    c.post("/api/signup", json={"username": "asker_" + secrets.token_hex(4), "password": PW})
    return c


def fake_answer(question):
    return ("God is near to you in this. Cast your worry on Him, because He cares "
            "for you (1 Peter 5:7). Check the Anxiety & Worry card.")


def test_ask_off_without_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    c = signed_client()
    r = c.post("/api/ask", json={"question": "I am worried about school"})
    assert r.status_code == 503, "no key, feature rests"


def test_ask_requires_signin(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr(ask_mod, "call_claude", fake_answer)
    nobody = TestClient(app)
    r = nobody.post("/api/ask", json={"question": "I am worried about school"})
    assert r.status_code == 401, "wallet and teens both protected by the door"


def test_ask_happy_path_mocked(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    seen = {}

    def spy(question):
        seen["q"] = question
        return fake_answer(question)

    monkeypatch.setattr(ask_mod, "call_claude", spy)
    c = signed_client()
    r = c.post("/api/ask", json={"question": "I can't stop worrying about my grades"})
    assert r.status_code == 200
    assert "1 Peter 5:7" in r.json()["answer"]
    assert seen["q"] == "I can't stop worrying about my grades"


def test_ask_validation(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr(ask_mod, "call_claude", fake_answer)
    c = signed_client()
    assert c.post("/api/ask", json={"question": "a"}).status_code == 422, "too short"
    assert c.post("/api/ask", json={"question": "x" * 501}).status_code == 422, "too long"


def test_ask_daily_limit(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr(ask_mod, "call_claude", fake_answer)
    monkeypatch.setattr(ask_mod, "DAILY_LIMIT", 2)
    c = signed_client()
    assert c.post("/api/ask", json={"question": "question one here"}).status_code == 200
    assert c.post("/api/ask", json={"question": "question two here"}).status_code == 200
    assert c.post("/api/ask", json={"question": "question three here"}).status_code == 429, "wallet fence"


def test_ask_upstream_failure(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    def boom(question):
        raise RuntimeError("upstream down")

    monkeypatch.setattr(ask_mod, "call_claude", boom)
    c = signed_client()
    r = c.post("/api/ask", json={"question": "hello out there"})
    assert r.status_code == 502, "friendly failure, no crash"
