# Kindling
## Product Requirements Document (PRD)

*A Bible guidance app for teenagers. Verses, plain talk, and real hope for real struggles.*

**Version 1.0 | July 25, 2026 | Written for Shandy**

---

## 1. What is a PRD, and why do we have one?

A PRD is a blueprint. Before a builder swings a hammer, they look at the drawing. This document is our drawing. It says what we are building, who it is for, what parts we get to borrow for free, and the order we build things in.

In restaurant terms: this is the plan you sketch before you open the food stand. What food do we sell? Who are our customers? Where do we buy ingredients? When do we grow into a real restaurant?

---

## 2. What we are building

**Kindling** is a web app where a teenager can tap a topic they are wrestling with, like **Identity**, **Anxiety**, or **Depression**, and get three things:

1. **God's Word.** Hand-picked Bible verses that speak straight to that struggle.
2. **Plain talk.** A short, warm explanation of what those verses mean for their life, written the way a caring youth leader would say it.
3. **A next step.** A simple thought or action to carry into their day.

Each topic lives on a **card**, just like your Genesis App pattern. We start with the Identity card and grow the deck over time.

Every card also carries a light **"Teach This"** section: three discussion questions so a parent, coach, or youth leader can turn any card into a 10-minute group conversation. You chose "both, kept light," so teens come first and leaders get a helpful corner on every card.

**The name:** Kindling. Small sticks that start big fires. Perfect for an app that sparks faith in young hearts. (Easy to rename later if you ever want to.)

---

## 3. Who it is for

| Person | What they need | How Kindling helps |
|---|---|---|
| **The teen** (13 to 18) | Fast, honest help that meets them where they are | Tap a topic, read verses in modern English, feel seen |
| **The leader** (parent, coach, youth pastor) | A ready-made way to open a conversation | "Teach This" questions on every card |
| **You and Dawn** | A simple app you can grow and share with your schools and community | Phased plan, quick win today, room to grow |

---

## 4. The features, card by card

### The deck (12 cards and growing)

1. **Identity** (the flagship card, who God says I am)
2. **Anxiety and Worry**
3. **Depression and Sadness**
4. **Loneliness**
5. **Fear and Courage**
6. **Anger**
7. **Friendship and Peer Pressure**
8. **Purpose and My Future**
9. **Forgiveness** *(added in Phase 2)*
10. **Self-Worth and Body Image** *(added in Phase 2)*
11. **Family** *(added in Phase 2)*
12. **Temptation** *(added in Phase 2)*

Backlog for later cards: Gratitude, Grief, Doubt, Social Media and Comparison.

### What every card holds

- A short intro in plain words (2 to 3 sentences)
- 6 to 8 hand-picked verses, shown in the **Berean Standard Bible** by default
- A translation switch: **BSB, WEB, or KJV** (all three, like you asked)
- "What this means for you," a short devotional paragraph
- "Teach This," 3 discussion questions for leaders
- A "next step" challenge

### App-wide features

- **Verse of the Day** on the home screen
- Clean, phone-first design (teens live on phones)
- **Care note:** the Anxiety, Depression, and Loneliness cards carry a gentle footer: "If the weight feels too heavy, tell a parent, pastor, or counselor. In the US you can call or text 988 anytime." The app points to Scripture and to real people. It never replaces them.

---

## 5. What we found that we can reuse (the research)

Great news: almost every ingredient is free. Here is the shopping list.

### Bible text (the main ingredient)

| Source | What it is | Cost | Why it matters |
|---|---|---|---|
| [Free Use Bible API (helloao)](https://bible.helloao.org/) | 1,000+ translations as simple JSON. No key, no limits, no copyright walls. Partners directly with the Berean Bible team. | Free | **Our main supplier.** Has BSB, WEB, and KJV. |
| [bible-api.com](https://bible-api.com/) | Tiny no-key API, WEB by default | Free | Backup supplier |
| [scrollmapper/bible_databases](https://github.com/scrollmapper/bible_databases) | The whole Bible as ready-made database files (SQL, JSON, CSV), 140+ translations plus cross-references | Free | **Phase 2.** We pour this straight into our Postgres pantry so the app owns its own Bible text. |
| [wldeh/bible-api](https://github.com/wldeh/bible-api) | CDN-hosted Bible JSON, 200+ versions | Free | Another backup |

**Licensing, in plain words:** Bible translations are like recipes. Some are trademarked family secrets (NIV, ESV) that cost money to serve. Ours are free-to-everyone recipes:

- **Berean Standard Bible (BSB):** placed fully in the public domain on April 30, 2023 ([their license page](https://berean.bible/licensing.htm)). Modern, readable, teen-friendly. Our default.
- **World English Bible (WEB):** public domain, modern-ish English.
- **King James Version (KJV):** public domain in the US, the classic.

No permission slips, no bills, ever. That is a huge win most Bible apps do not get.

### Topic-to-verse maps (the seasoning)

- [Nave's Topical Bible](https://www.ccel.org/ccel/nave/bible.html): 20,000+ topics mapped to verses, public domain since 1896. Good raw material.
- [BradyStephenson/bible-data](https://github.com/BradyStephenson/bible-data): Nave's as a clean CSV file, free license.
- **Our choice for Phase 1:** hand-pick the verses ourselves. An 1896 index does not have a card called "Social Media and Comparison." For teen topics, a loving human touch (you, Dawn, and me) beats an old index. Nave's becomes a helper in later phases when we add a topic search.

### The four frameworks (our cookbooks for how to work)

You gave me four playbooks. Here is what each one is and how we use it:

| Framework | What it is, in plain words | How Kindling uses it |
|---|---|---|
| [Superpowers](https://github.com/obra/superpowers) | A discipline system for coding agents: brainstorm first, write tests first, work in small safe steps | I brainstormed and asked you questions before writing code. Each feature gets a test. |
| [Get Shit Done (GSD)](https://github.com/gsd-build/get-shit-done) | A "spec first, then phases" system. Write the plan, split it into phases, verify each phase before the next | This very PRD and the phased roadmap below follow the GSD way. |
| [Metaswarm](https://github.com/dsifry/metaswarm) | A team of specialist AI reviewers with quality gates. Code is never merged without review | Our QA gate and Security gate (testing levels 4 and 5) come from this. I put on a "reviewer hat" and check my own work like a second chef tasting the dish. |
| [Claude Agents Library](https://github.com/aiagentskit/claude-agents-library) | 34 ready-made specialist roles (rapid prototyper, API tester, backend architect) | I wear these hats at the right moments: rapid-prototyper today, api-tester during testing, backend-architect in Phase 2. |

One honest note: these are plugins for Claude Code, the developer tool. In our Cowork sessions I cannot literally install them, so I follow their methods faithfully instead. Same recipes, same kitchen discipline. If you ever open Claude Code, we can install them for real with one command each.

### Testing tools

- **Pytest:** the taste-tester for our Python kitchen. Free.
- **Playwright:** a robot that opens the app in a browser and clicks like a real teen would. Free.
- **[Playwright CRX](https://github.com/ruifigueira/playwright-crx):** a Chrome extension that records your own clicks and turns them into test scripts. When you click through Kindling yourself, it can write the test for you. Free.

### Hosting and storage

- **[Railway](https://docs.railway.com/guides/fastapi):** where the app lives, your pick. Their docs have a FastAPI guide that matches our stack. Deploy is two commands: `railway init` then `railway up`.
- **Postgres on Railway:** our pantry, added in Phase 2 (one click on Railway).
- **Cloudflare R2:** our walk-in freezer for files (share images, audio). Enters in Phase 4 when we first have files worth freezing.

---

## 6. The stack (our kitchen equipment)

| Piece | Tool | Restaurant part |
|---|---|---|
| Backend | **FastAPI** (Python) | The kitchen that takes orders and plates food |
| Frontend | One clean HTML page (mobile-first) | The dining room |
| Content | A simple JSON file in Phase 1, **Postgres** in Phase 2 | Recipe cards taped to the wall today, a real pantry soon |
| Bible text | Free Use Bible API (helloao) | The ingredient supplier who delivers for free |
| Hosting | **Railway** | The building and the lot |
| File storage | **Cloudflare R2** (Phase 4) | The walk-in freezer |
| Tests | Pytest + Playwright | The health inspector and the taste-tester |

**Why FastAPI?** It is Python (which plays perfectly with Pytest, your testing pick), it is beginner-friendly to read, Railway loves it, and it grows gracefully from food stand to full restaurant without changing kitchens.

---

## 7. The roadmap (from food stand to full restaurant)

### Phase 1: The Food Stand ✅ SHIPPED July 25, 2026

*One counter, one cook, food people actually want.*

**What we build today:**

- FastAPI app serving one polished, phone-first page
- 8 topic cards, Identity first, each with verses, plain talk, Teach This questions, and a next step
- Translation switch (BSB default, WEB, KJV)
- Verse of the Day
- Care note on the heavy cards
- Verse text pulled live from the Free Use Bible API

**What we do NOT build today:** logins, database, AI chat. A food stand does not need a walk-in freezer.

**Tests today:** Level 1 smoke tests (does the page load? do cards open? any errors?) with Pytest and Playwright.

**Done when:** you can open it on your phone, tap Identity, and read Scripture speaking to a teen's heart.

### Phase 2: The Food Truck ✅ BUILT July 25, 2026 (deploy waits on your go)

*Same food, real equipment, ready to drive anywhere.*

- ✅ Database pantry with **all 93,286 verses** of BSB, KJV, and WEB packed into the app itself (no outside server needed, ever)
- ✅ Works two ways with zero code changes: **Postgres** on Railway, simple SQLite on a laptop
- ✅ **Bible reader** (all 66 books, chapter by chapter, prev/next) and **whole-Bible search**, as new Read and Search tabs
- ✅ Grew to **12 cards** (Forgiveness, Self-Worth and Body Image, Family, Temptation joined the deck)
- ✅ Tests: levels 2 and 3 run against a real stocked database (18 tests total)
- ⏳ **Deploy to Railway** with the CLI: ready and waiting, happens the moment you ask
- One smart simplification: the card words stay in a simple file (they are ours and change with the app), while the 93,286-verse Bible lives in the database pantry. Cards move to the database in Phase 3 when accounts and favorites need them there.

### Phase 3: The Restaurant with One Employee ✅ BUILT July 25, 2026

*Regulars have names now.*

- ✅ Accounts with a privacy-first design: **username and password only**. No email, no real name, no birthday. The less we know about a teen, the less anyone could misuse.
- ✅ **Heart any verse** (on cards and in the Bible reader) and see saved verses on the Me tab
- ✅ **Private journal** ("What is God showing you?"), owner-only, tested against snooping
- ✅ **Streak flame**: days in a row spent with the Word
- ✅ **QA gate (level 4) and Security gate (level 5)** run and documented in `kindling/docs/GATES.md`: bcrypt-hashed passwords, locked-down cookies, login throttling, injection and XSS tests, cross-user privacy tests
- Test suite now at **29 tests**, all passing
- Simple plans ("7 days on Identity") slide to Phase 4, streaks landed first

### Phase 4: Full Restaurant, Front and Back of House ✅ BUILT July 25, 2026

*A staff, a menu that changes, people driving from the next town.*

- ✅ **Ask Kindling:** a teen types what they are facing and gets warm, Scripture-grounded direction with tappable verse links. Carefully fenced: sign-in required, 10 questions a day per account, crisis language always points to trusted adults and 988, and the AI key lives only on the server. The tab stays hidden until you add an Anthropic API key on Railway, so it costs nothing until you say so.
- ✅ **Leader lesson mode:** one tap on any card builds a full 15-minute lesson (open, read together, talk, questions, challenge, close). Print it or copy it as text for the group chat. Built for you, Dawn, coaches, and youth leaders.
- ✅ **Shareable verse cards:** any verse becomes a beautiful ember-styled image, drawn right on the teen's phone. On phones it opens the share sheet; on computers it downloads. Smart simplification: no storage needed at all, so **Cloudflare R2** waits until something truly needs server-side storage (like audio). No bill, no setup, same beauty.
- Still on the menu for later: licensed translations (NIV, NLT) via API.Bible, reading plans, Spanish.

### Someday shelf

Spanish translations (helloao has them free), audio verses, church/school group codes, streak reminders.

---

## 8. The testing plan (your hierarchy, mapped)

Light to heavy, exactly as you laid out:

| Level | Test | When it runs |
|---|---|---|
| 0 | **Playwright CRX + Pytest** as our base tools | Every phase |
| 1 | **Smoke test:** page loads, no JS errors, cards visible | Phase 1, today |
| 2 | **Functional test:** Playwright clicks with pretend (mocked) data | Phase 2 |
| 3 | **Integration test:** Playwright against real APIs and real database | Phase 2 |
| 4 | **QA gate:** code quality, error handling, database health, speed checklist | Phase 3, and before every deploy |
| 5 | **Security gate:** input validation, safe logins, data protection checklist | Phase 3, when accounts arrive |

Restaurant version: taste one dish, then taste the whole menu, then let the health inspector in, then hire security for the door.

---

## 9. Care, safety, and heart

This app touches tender places in young lives, so four commitments are baked in:

1. **Scripture first, always.** Kindling points to the Bible and to trusted adults. It never plays counselor.
2. **Crisis care.** Heavy cards carry the 988 line and a nudge toward real people. Non-negotiable, in from day one.
3. **Sound and simple.** Devotional words stay warm, biblical, and non-denominational. You and Dawn review every card's words before we call it done. You two are the shepherds of the tone.
4. **Every teen, the same words.** Kindling is gender neutral: everything we write (intros, meanings, questions, next steps, app labels) speaks to every teen the same. An automated language guard test scans every card and fails the build if gendered wording ever sneaks in. One careful line: Scripture quotes stay exactly as translated, word for word. Our words flex; God's Word we do not edit.

---

## 10. Risks, told straight

- **The free API could someday slow or stop.** Fix: Phase 2 moves all Bible text into our own Postgres. Risk fully retired by owning the pantry.
- **AI-written devotionals could miss the mark.** Fix: you and Dawn review every card. Human hearts approve what human hearts will read.
- **Scope creep** (the urge to build the full restaurant on day one). Fix: the phase gates. We do not buy the freezer before we sell the first taco.

---

## 11. What I need from you

**Today:** nothing but your green light. Every ingredient is free and I have all of them.

**When we deploy (Phase 2):** a free account at railway.com and about 5 minutes to log in to the Railway CLI. I will walk you through it click by click, exactly, when the moment comes.

**Ongoing:** your and Dawn's eyes on the words. You know teens' hearts through 15 years of working with schools. That review is the secret sauce no framework can replace.

---

## 12. Little glossary (plain words for the fancy words)

- **PRD:** the blueprint you are reading right now.
- **API:** a waiter between two programs. Our app asks the Bible API for John 3:16, and the waiter brings it back on a tray.
- **JSON:** the neat little order-ticket format the waiter writes in.
- **FastAPI:** the Python kitchen that runs our app.
- **Postgres:** a big organized pantry (a database) where data lives in labeled rows.
- **Deploy:** moving the food stand from our driveway to a real street corner (putting the app on the internet).
- **Smoke test:** plug it in, does smoke come out? The quickest "is it alive?" check.
- **Mocked test:** practicing with plastic food so the test never depends on the real supplier.
- **Public domain:** belongs to everyone, free forever, no permission needed.

---

*"Your word is a lamp to my feet and a light to my path." Psalm 119:105 (BSB)*
