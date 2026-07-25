"""
The pantry door. One place that decides which database Kindling talks to.

On Railway, the DATABASE_URL environment variable points at Postgres.
On a laptop (or in tests), with no DATABASE_URL, we use a simple SQLite
file instead. Same shelves, same labels, different building. The code
above this layer never has to care which one it is.
"""
import os
from datetime import datetime, timezone

from sqlalchemy import (Column, DateTime, Date, Integer, String, Text,
                        UniqueConstraint, Index, create_engine, func, select)
from sqlalchemy.orm import DeclarativeBase, Session


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SQLITE = "sqlite:///" + os.environ.get(
    "KINDLING_SQLITE", os.path.join(ROOT, "data", "kindling.db"))


def database_url() -> str:
    url = os.environ.get("DATABASE_URL", DEFAULT_SQLITE)
    # Railway hands out postgres:// but SQLAlchemy wants postgresql://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


class Base(DeclarativeBase):
    pass


class BibleVerse(Base):
    __tablename__ = "bible_verses"
    id = Column(Integer, primary_key=True)
    translation = Column(String(8), nullable=False)
    book = Column(String(40), nullable=False)
    book_order = Column(Integer, nullable=False)
    chapter = Column(Integer, nullable=False)
    verse = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    __table_args__ = (
        UniqueConstraint("translation", "book", "chapter", "verse",
                         name="uq_verse"),
        Index("ix_read", "translation", "book_order", "chapter", "verse"),
    )


class User(Base):
    """One teen. On purpose we keep almost nothing: no email, no real name."""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(20), nullable=False, unique=True)
    password_hash = Column(String(100), nullable=False)
    created_at = Column(DateTime, nullable=False, default=utcnow)


class SessionToken(Base):
    """A signed-in visit. The browser holds the token in a locked cookie."""
    __tablename__ = "session_tokens"
    token = Column(String(64), primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=utcnow)
    expires_at = Column(DateTime, nullable=False)


class Favorite(Base):
    """A verse a teen hearted, with the text saved as they read it."""
    __tablename__ = "favorites"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    ref = Column(String(40), nullable=False)
    translation = Column(String(8), nullable=False, default="BSB")
    text = Column(Text, nullable=False)
    topic_id = Column(String(20), nullable=True)
    created_at = Column(DateTime, nullable=False, default=utcnow)
    __table_args__ = (UniqueConstraint("user_id", "ref", name="uq_fav"),)


class JournalEntry(Base):
    """Private words between a teen and God. Nobody else's business."""
    __tablename__ = "journal_entries"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=utcnow)


class Activity(Base):
    """One row per day a teen opened Kindling. Powers the streak flame."""
    __tablename__ = "activity"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    day = Column(Date, nullable=False)
    __table_args__ = (UniqueConstraint("user_id", "day", name="uq_day"),)


_engine = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(database_url(), future=True)
    return _engine


def bible_ready() -> bool:
    """Is the pantry stocked? True when verses are actually loaded."""
    try:
        with Session(get_engine()) as s:
            n = s.execute(select(func.count()).select_from(BibleVerse)).scalar()
            return bool(n and n > 1000)
    except Exception:
        return False
