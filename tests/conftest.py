"""
Test setup that runs before anything else.
Points the app at a local SQLite pantry and stocks it if empty,
so the Bible reader and search tests run against real data.
"""
import os
import sys

os.environ.setdefault("KINDLING_SQLITE", "/tmp/kindling.db")
os.environ.setdefault("AUTO_IMPORT", "0")  # tests stock the pantry themselves

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from app.db import bible_ready  # noqa: E402


def _stock_if_needed():
    if not bible_ready():
        from scripts.import_bible import main as stock
        stock()


_stock_if_needed()
