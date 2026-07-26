"""
Kindling, Phase 2 (the Food Truck).
FastAPI kitchen: topic cards, verse of the day, plus a full Bible reader
and search served from our own database pantry.
"""
import json
import os
import threading
from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.accounts import router as accounts_router
from app.ask import ask_enabled, router as ask_router
from app.db import Base, BibleVerse, bible_ready, get_engine
from app.grow import router as grow_router
from app.serve import router as serve_router

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_PATH = os.path.join(ROOT, "data", "topics.json")
STATIC_DIR = os.path.join(HERE, "static")


@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(get_engine())  # build any missing shelves
    auto_stock_pantry()
    yield


app = FastAPI(title="Kindling", version="0.5.0",
              description="Bible guidance for teenagers. Verses, plain talk, real hope.",
              lifespan=lifespan)
app.include_router(accounts_router)
app.include_router(ask_router)
app.include_router(serve_router)
app.include_router(grow_router)

with open(DATA_PATH, encoding="utf-8") as f:
    DATA = json.load(f)

ALL_VERSES = [
    {"topic_id": t["id"], "topic": t["title"], **v}
    for t in DATA["topics"]
    for v in t["verses"]
]

TRANSLATION_CODES = list(DATA["translations"].keys())

# Once the pantry is confirmed stocked, remember it (sticky yes).
_BIBLE_OK = {"ok": False}


def bible_ok() -> bool:
    if not _BIBLE_OK["ok"]:
        _BIBLE_OK["ok"] = bible_ready()
    return _BIBLE_OK["ok"]


def auto_stock_pantry():
    """On a fresh deploy the database is empty. Stock it in the background
    so the app boots fast and the reader lights up a moment later."""
    if os.environ.get("AUTO_IMPORT", "1") == "0" or bible_ok():
        return

    def run():
        try:
            import sys
            sys.path.insert(0, ROOT)
            from scripts.import_bible import main as stock
            stock()
            _BIBLE_OK["ok"] = bible_ready()
        except Exception as e:  # pantry stays closed; cards still work
            print(f"[kindling] pantry stocking failed: {e}")

    threading.Thread(target=run, daemon=True).start()


def check_translation(tr: str) -> str:
    if tr not in TRANSLATION_CODES:
        raise HTTPException(status_code=404, detail=f"Unknown translation '{tr}'")
    return tr


# ---------------------------------------------------------------- basics

@app.get("/health")
def health():
    """Is the stove on?"""
    return {"status": "ok", "cards": len(DATA["topics"]), "bible": bible_ok()}


@app.get("/api/topics")
def topics():
    """The whole menu: every card with verses in all translations."""
    payload = dict(DATA)
    payload["bible_enabled"] = bible_ok()
    payload["accounts_enabled"] = True
    payload["ask_enabled"] = ask_enabled()
    payload["serve_enabled"] = True
    payload["grow_enabled"] = True
    return JSONResponse(payload)


@app.get("/api/topics/{topic_id}")
def topic(topic_id: str):
    for t in DATA["topics"]:
        if t["id"] == topic_id:
            return t
    raise HTTPException(status_code=404, detail=f"No card named '{topic_id}'")


@app.get("/api/votd")
def verse_of_the_day():
    idx = date.today().toordinal() % len(ALL_VERSES)
    return ALL_VERSES[idx]


# ---------------------------------------------------------------- bible reader

@app.get("/api/bible/books")
def bible_books(tr: str = Query("BSB")):
    """All 66 books with chapter counts, in Bible order."""
    check_translation(tr)
    if not bible_ok():
        raise HTTPException(status_code=503, detail="Bible is still being stocked. Try again in a minute.")
    with Session(get_engine()) as s:
        rows = s.execute(
            select(BibleVerse.book, BibleVerse.book_order,
                   func.max(BibleVerse.chapter))
            .where(BibleVerse.translation == tr)
            .group_by(BibleVerse.book, BibleVerse.book_order)
            .order_by(BibleVerse.book_order)
        ).all()
    return {"translation": tr,
            "books": [{"book": b, "order": o, "chapters": c} for b, o, c in rows]}


@app.get("/api/bible/passage")
def bible_passage(book: str, chapter: int, tr: str = Query("BSB")):
    """One chapter of Scripture, with prev/next pointers."""
    check_translation(tr)
    if not bible_ok():
        raise HTTPException(status_code=503, detail="Bible is still being stocked. Try again in a minute.")
    with Session(get_engine()) as s:
        rows = s.execute(
            select(BibleVerse.verse, BibleVerse.text)
            .where(BibleVerse.translation == tr, BibleVerse.book == book,
                   BibleVerse.chapter == chapter)
            .order_by(BibleVerse.verse)
        ).all()
        if not rows:
            raise HTTPException(status_code=404, detail=f"No text for {book} {chapter} ({tr})")
        # neighbors for prev/next buttons
        info = s.execute(
            select(BibleVerse.book_order, func.max(BibleVerse.chapter))
            .where(BibleVerse.translation == tr, BibleVerse.book == book)
            .group_by(BibleVerse.book_order)
        ).one()
        order, max_ch = info
        prev_ref = next_ref = None
        if chapter > 1:
            prev_ref = {"book": book, "chapter": chapter - 1}
        else:
            pb = s.execute(
                select(BibleVerse.book, func.max(BibleVerse.chapter))
                .where(BibleVerse.translation == tr, BibleVerse.book_order == order - 1)
                .group_by(BibleVerse.book)
            ).first()
            if pb:
                prev_ref = {"book": pb[0], "chapter": pb[1]}
        if chapter < max_ch:
            next_ref = {"book": book, "chapter": chapter + 1}
        else:
            nb = s.execute(
                select(BibleVerse.book)
                .where(BibleVerse.translation == tr, BibleVerse.book_order == order + 1)
                .limit(1)
            ).first()
            if nb:
                next_ref = {"book": nb[0], "chapter": 1}
    return {"translation": tr, "book": book, "chapter": chapter,
            "verses": [{"v": v, "t": t} for v, t in rows],
            "prev": prev_ref, "next": next_ref}


@app.get("/api/search")
def search(q: str = Query(min_length=3, max_length=100), tr: str = Query("BSB")):
    """Find verses containing a word or phrase. Case does not matter."""
    check_translation(tr)
    if not bible_ok():
        raise HTTPException(status_code=503, detail="Bible is still being stocked. Try again in a minute.")
    needle = q.strip()
    if len(needle) < 3:
        raise HTTPException(status_code=422, detail="Give me at least 3 letters to hunt for.")
    like = "%" + needle.replace("%", "").replace("_", "") + "%"
    with Session(get_engine()) as s:
        rows = s.execute(
            select(BibleVerse.book, BibleVerse.chapter, BibleVerse.verse, BibleVerse.text)
            .where(BibleVerse.translation == tr, BibleVerse.text.ilike(like))
            .order_by(BibleVerse.book_order, BibleVerse.chapter, BibleVerse.verse)
            .limit(50)
        ).all()
    return {"translation": tr, "query": needle, "count": len(rows),
            "results": [{"book": b, "chapter": c, "verse": v, "text": t}
                        for b, c, v, t in rows]}


@app.get("/")
def home():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))
