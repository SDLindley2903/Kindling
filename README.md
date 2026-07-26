# Kindling (Phase 4: the Full Restaurant)

*Bible guidance for teenagers. Verses, plain talk, and real hope. Gender neutral by design.*

The full build: 12 topic cards, the whole Bible in three translations with reader
and search, accounts (username + password only, nothing else collected), hearted
verses, a private journal, streaks, printable leader lessons, shareable verse
images, and Ask Kindling (AI guidance, off until an `ANTHROPIC_API_KEY` is set).
See `docs/GATES.md` for the QA and security inspection report.

## The fastest way to see it

Double-click **`Kindling.html`** (it sits one folder up, next to this `kindling` folder).
It opens in your browser and works with no internet and no setup. That file IS the app,
packed into a takeout box. (The takeout box carries the 12 cards. The full Bible reader
and search need the real server below, because they lean on the database pantry.)

## What is in this folder

| Folder / file | What it is |
|---|---|
| `app/main.py` | The kitchen. FastAPI server: cards, verse of the day, Bible reader, search. |
| `app/accounts.py` | The front desk. Sign up, sign in, favorites, journal, streaks. |
| `app/ask.py` | The counselor's referral desk. Ask Kindling, fenced and key-gated. |
| `app/serve.py` | The service hours ledger. Logging, totals, and export. |
| `app/grow.py` | The daily rhythm tracker. Streaks, heat map, and the checklist. |
| `app/db.py` | The pantry door. Postgres on Railway, SQLite on a laptop, same code either way. |
| `app/static/index.html` | The dining room. The page teens see: Cards, Read, and Search tabs. |
| `data/topics.json` | The recipe cards. 12 topics, 76 passages, each in BSB, WEB, and KJV. |
| `data/bible/*.jsonl.gz` | Three complete Bibles (93,286 verses), packed and owned by the app. |
| `scripts/build_content.py` | The prep cook. Rebuilds `topics.json` from real Bible text. |
| `scripts/prepare_bible_data.py` | The supplier run. Repacks the full Bibles from source. |
| `scripts/import_bible.py` | The stocker. Loads the Bibles into the database. Safe to rerun. |
| `scripts/make_standalone.py` | The takeout packer. Rebuilds `Kindling.html`. |
| `tests/` | The taste testers. 18 tests: smoke (level 1), functional + integration (levels 2-3), and the gender-neutral language guard. |
| `railway.json` | The address card for Railway. Deploy-ready. |

## Running the real server

```bash
pip install -r requirements.txt
python3 scripts/import_bible.py   # stock the pantry (first time only; auto-runs on deploy too)
uvicorn app.main:app --reload
# then open http://localhost:8000
```

## Running the tests

```bash
pytest tests/ -v
```

## Rebuilding content from scratch (only if ever needed)

The app is fully self-contained: `data/topics.json` and `data/bible/*.jsonl.gz`
are already built and saved. The two prep scripts only matter if we ever want to
rebuild them, and they read the original Bible sources from these free repos:

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/scrollmapper/bible_databases.git
git clone --depth 1 https://github.com/TehShrike/world-english-bible.git
# then point BSB_PATH, KJV_PATH, WEB_DIR at the downloaded files and run the scripts
```

## Language policy

Everything we write speaks to every teen the same. A test (`tests/test_language.py`)
fails the build if gendered wording sneaks into our copy. Scripture quotes are the one
deliberate exception: the Bible's text is never edited, not one word.

## Scripture licensing

Berean Standard Bible (public domain, 2023), World English Bible (public domain),
King James Version (public domain in the US). No permission needed, ever.
