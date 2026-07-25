# Kindling Quality Gates
*Levels 4 and 5 of our testing hierarchy. The health inspector's clipboard.*

Last run: July 25, 2026 (Phase 5). Test suite: 48 automated tests, all passing.

## Level 4: QA Gate

| Check | Status | Notes |
|---|---|---|
| Code quality: small modules, one job each | PASS | `main.py` (kitchen), `db.py` (pantry door), `accounts.py` (front desk), scripts do prep work |
| Error handling: bad input returns friendly errors, not crashes | PASS | 404s for unknown cards/books/chapters, 422s with plain messages for bad input, 503 while pantry stocks |
| Database: indexed for its queries | PASS | Bible reads hit the `(translation, book_order, chapter, verse)` index; favorites and journal hit `user_id` indexes; uniqueness enforced in the database, not just the code |
| Database: safe to redeploy | PASS | Imports are idempotent (safe to run twice); tables auto-create on boot; app boots fine and serves cards even if Bible stocking is still running |
| Performance: response sizes and limits | PASS | Search capped at 50 rows, favorites at 500, journal at 200; biggest payload (topics.json) about 130 KB; whole-Bible search on 31k rows returns in milliseconds |
| No dead dependencies | PASS | Six runtime packages, each earning its place |
| Frontend: works without build tools, no console errors | PASS | Vanilla JS, syntax-checked; all rendering escapes user text |

## Level 5: Security Gate

| Check | Status | Notes |
|---|---|---|
| Input validation on every field | PASS | Username shape (3-20, letters/numbers/underscore), password length (8-72), journal cap (4000), favorite ref/text caps; tested with injection-shaped input |
| SQL injection | PASS | All queries go through the ORM with bound parameters; zero hand-built SQL; injection-string username rejected by validation before touching the database |
| XSS (script sneaking into pages) | PASS | Every piece of user or Bible text is escaped by `esc()` before rendering; stored `<script>` test confirms it stays harmless data |
| Passwords | PASS | bcrypt hashed with per-password salt; never logged; test proves the plain password is absent from the database |
| Sessions | PASS | Random 256-bit server-side tokens; httponly + samesite=lax cookie; secure flag auto-on behind HTTPS (Railway); logout revokes server-side; 30-day expiry |
| Brute force | PASS | 5 failed logins locks that username for a minute (tested); generic "wrong username or password" message leaks nothing |
| Data protection / privacy | PASS | We collect a username and a password hash. Nothing else. No email, no name, no tracking. Journals and favorites are owner-only (cross-user access tested and denied) |
| Secrets management | PASS | No secrets in code; DATABASE_URL and ANTHROPIC_API_KEY come from the environment on Railway |
| Service hours integrity | PASS | Totals verified by test (hours, categories, school-year rollups); no future dates; 0-24 hour bounds; unknown categories fall back safely; owner-only access tested against cross-account reads and deletes; CSV export requires sign-in |
| Ask Kindling (AI) fences | PASS | Sign-in required; 10 questions per day per account; 500-character question cap; the AI key never reaches the browser; system prompt enforces crisis care (trusted adult + 988), gender-neutral language, and refuses prompt games; friendly 502/503 instead of crashes; fully covered by mocked tests |

## Honest footnotes (the inspector's margin notes)

- The login throttle lives in the app's memory, which is perfect for one Railway
  instance (our world for a long while). If Kindling ever runs many copies at
  once, move the throttle into Postgres or Redis.
- CSRF risk is low (samesite cookie + JSON-only endpoints), and rides to zero
  when we add an origin check in a later phase. Noted for Phase 4.
- Railway Postgres backups: turn on automatic backups in the Railway dashboard
  after we deploy. One click, real peace of mind.
- Password resets do not exist on purpose (we have no email to send to). A teen
  who forgets a password makes a fresh account. Simple beats risky at this size.
