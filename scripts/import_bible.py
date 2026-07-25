#!/usr/bin/env python3
"""
Stocks the pantry: loads the three packed Bibles from data/bible/ into the
database (Postgres on Railway, SQLite on a laptop). Safe to run twice; a
translation that is already fully stocked is skipped.

Run:  python3 scripts/import_bible.py
"""
import gzip
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from sqlalchemy import delete, func, select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402
from app.db import Base, BibleVerse, get_engine  # noqa: E402

BIBLE_DIR = os.path.join(ROOT, "data", "bible")
TRANSLATIONS = ["BSB", "KJV", "WEB"]
CHUNK = 5000


def rows_for(code):
    path = os.path.join(BIBLE_DIR, f"{code}.jsonl.gz")
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            yield {"translation": code, "book": r["b"], "book_order": r["o"],
                   "chapter": r["c"], "verse": r["v"], "text": r["t"]}


def main():
    engine = get_engine()
    Base.metadata.create_all(engine)
    t0 = time.time()
    with Session(engine) as s:
        for code in TRANSLATIONS:
            want = sum(1 for _ in rows_for(code))
            have = s.execute(select(func.count()).select_from(BibleVerse)
                             .where(BibleVerse.translation == code)).scalar()
            if have == want:
                print(f"{code}: already stocked ({have:,} verses), skipping.")
                continue
            if have:
                print(f"{code}: partial ({have:,}/{want:,}), restocking fresh.")
                s.execute(delete(BibleVerse).where(BibleVerse.translation == code))
                s.commit()
            batch = []
            n = 0
            for row in rows_for(code):
                batch.append(row)
                if len(batch) >= CHUNK:
                    s.bulk_insert_mappings(BibleVerse, batch)
                    n += len(batch)
                    batch = []
            if batch:
                s.bulk_insert_mappings(BibleVerse, batch)
                n += len(batch)
            s.commit()
            print(f"{code}: stocked {n:,} verses.")
        total = s.execute(select(func.count()).select_from(BibleVerse)).scalar()
    print(f"Pantry total: {total:,} verses in {time.time()-t0:.1f}s. Done.")


if __name__ == "__main__":
    main()
