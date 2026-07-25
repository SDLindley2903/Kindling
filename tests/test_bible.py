"""
Levels 2-3: functional and integration tests for the Bible reader and search,
running against a real stocked database (SQLite locally, Postgres on Railway).
Run with:  pytest tests/ -v
"""
import os
import sys

from fastapi.testclient import TestClient

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from app.main import app  # noqa: E402

client = TestClient(app)


def test_bible_is_enabled():
    r = client.get("/api/topics")
    assert r.json()["bible_enabled"] is True
    assert client.get("/health").json()["bible"] is True


def test_books_shelf():
    for tr in ("BSB", "WEB", "KJV"):
        r = client.get(f"/api/bible/books?tr={tr}")
        assert r.status_code == 200
        books = r.json()["books"]
        assert len(books) == 66, f"{tr} should hold all 66 books"
        assert books[0]["book"] == "Genesis"
        assert books[-1]["book"] == "Revelation"
        assert books[18]["book"] == "Psalms" and books[18]["chapters"] == 150


def test_passage_john_3():
    r = client.get("/api/bible/passage?tr=BSB&book=John&chapter=3")
    assert r.status_code == 200
    d = r.json()
    assert len(d["verses"]) == 36
    v16 = next(v for v in d["verses"] if v["v"] == 16)
    assert "For God so loved the world" in v16["t"]
    assert d["prev"] == {"book": "John", "chapter": 2}
    assert d["next"] == {"book": "John", "chapter": 4}


def test_passage_edges_and_book_hops():
    first = client.get("/api/bible/passage?tr=KJV&book=Genesis&chapter=1").json()
    assert first["prev"] is None, "nothing comes before Genesis 1"
    last = client.get("/api/bible/passage?tr=KJV&book=Revelation&chapter=22").json()
    assert last["next"] is None, "nothing comes after Revelation 22"
    hop = client.get("/api/bible/passage?tr=WEB&book=Malachi&chapter=4").json()
    assert hop["next"] == {"book": "Matthew", "chapter": 1}, "Old hops to New"


def test_passage_404s():
    assert client.get("/api/bible/passage?tr=BSB&book=Narnia&chapter=1").status_code == 404
    assert client.get("/api/bible/passage?tr=BSB&book=John&chapter=99").status_code == 404
    assert client.get("/api/bible/passage?tr=XYZ&book=John&chapter=3").status_code == 404


def test_search_finds_john_316():
    r = client.get("/api/search?tr=BSB&q=God so loved the world")
    assert r.status_code == 200
    d = r.json()
    hits = [(x["book"], x["chapter"], x["verse"]) for x in d["results"]]
    assert ("John", 3, 16) in hits


def test_search_case_does_not_matter():
    a = client.get("/api/search?tr=WEB&q=SHEPHERD").json()["count"]
    b = client.get("/api/search?tr=WEB&q=shepherd").json()["count"]
    assert a == b and a > 0


def test_search_guardrails():
    assert client.get("/api/search?tr=BSB&q=ab").status_code == 422, "too short"
    r = client.get("/api/search?tr=KJV&q=the")
    assert r.status_code == 200 and r.json()["count"] <= 50, "results are capped"
    weird = client.get("/api/search?tr=BSB&q=%25%25%25").status_code
    assert weird in (200, 422), "wildcards are neutralized, not crashing"
