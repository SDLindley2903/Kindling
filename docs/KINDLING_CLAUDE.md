# CLAUDE.md — Kindling

Teen Bible app. Anchor verse **Luke 24:32 (KJV)** — *"Did not our heart burn
within us..."* Tagline: **"Small sparks. Real fire."**

This file is the project brief a coding agent reads first. It captures the
vision and the plan. The **source code is added separately** (see the status
note below). Read this fully before touching anything.

---

## Status of this file

> ⚠️ **This is the project brief, not the codebase yet.**
> As of this writing, the Kindling source files live on another device and
> haven't been added to the repo. The sections marked **[FILL IN FROM SOURCE]**
> need to be completed once the real code is in place: tech stack, folder
> structure, build/run commands, and dependencies. Everything else below is the
> confirmed product vision and can be treated as the source of truth for *what
> Kindling is meant to be.*

---

## What Kindling is

A Bible app built for teenagers. Not a watered-down kids' app, and not an adult
devotional app with the edges filed off. Kindling is card-first, quick to open,
and built to turn a small daily spark into a real, lasting faith.

**Audience:** teens, both guys and girls. The design is deliberately not skewed
feminine or juvenile. It has to feel right in a 16-year-old's hand.

**Heart of it:** Luke 24:32. The burning heart. Small sparks, real fire. Every
design and copy decision should serve that feeling — momentum, warmth, something
catching and growing.

---

## The four v1 features

These four are the whole of version one. Ship these well before anything else
gets added.

1. **Cards** — the front door and the signature. Card-first design: short,
   tappable, daily spiritual content a teen can engage with in a minute. This is
   what makes Kindling feel different from a wall-of-text Bible app.

2. **Bible (KJV)** — a clean King James Version reader. Should work **offline**;
   the text is bundled, not dependent on a live connection.

3. **Prayer Journal** — a private space for teens to write and keep prayers.
   Personal, simple, theirs.

4. **Serve Time** — **the key differentiator.** Tracks service hours in a way
   teens can use for **scholarship and National Honor Society (NHS)
   applications.** No competitor is doing this. This is the feature that makes a
   parent, a youth pastor, or a guidance counselor say "you need this app."

---

## Why Kindling wins (competitive positioning)

Primary competitor: **WONDER** (by Revive Our Hearts).

Kindling's edges over WONDER, and they should never be sanded down:

- **Android from launch.** Not iOS-only. Meets teens on the phones they actually
  carry.
- **Offline operation.** Works at camp, on a retreat, in a basement youth room
  with no signal.
- **Card-first design for both genders.** Not skewed to one audience.
- **Serve Time.** The scholarship/NHS hour tracking nobody else offers.

The name **Kindling** is confirmed clean on both app stores.

---

## Design north star

- Warm, alive, catching-fire energy. Sparks to flame, never cold or clinical.
- Fast and light. A teen opens it, gets a spark, moves on with their day.
- Card-first everywhere it makes sense. Bite-sized beats walls of text.
- Feels made for a teenager, not handed down to one.

---

## [FILL IN FROM SOURCE] — complete once code is in the repo

- [ ] **Tech stack** — framework, language, native build approach. *(Do not
      assume. Confirm from the actual project files before writing a line.)*
- [ ] **Folder / file structure** — where screens, components, and the bundled
      KJV text live.
- [ ] **Build & run commands** — how to install, run locally, and build for
      Android (and iOS if applicable).
- [ ] **Dependencies** — packages in use and why.
- [ ] **Data & storage** — where the Prayer Journal and Serve Time data are kept,
      and how privacy is handled. *(Teen data. Handle with extra care.)*
- [ ] **Auth**, if any.

---

## Bug-fix protocol (once code is here)

1. **Reproduce and name the bug first.** Which feature (Cards, Bible, Prayer
   Journal, Serve Time), which screen, what's wrong, what's correct.
2. **Smallest safe change.** Fix the reported issue; don't refactor around it.
3. **Protect the four features.** v1 is exactly Cards, Bible (KJV), Prayer
   Journal, Serve Time. Don't add scope. Don't quietly drop a feature.
4. **Keep the offline promise.** The KJV reader must keep working with no
   connection. Don't introduce a live dependency into it.
5. **Guard teen data.** Prayer Journal and Serve Time hold personal content from
   minors. No third-party tracking, no leaking that data, no shortcuts.
6. **Android is a first-class citizen.** Never let a fix quietly break Android to
   make iOS easier.
7. **Verify before done.** Say what changed, what you checked, and confirm the
   four features still work.

## Things NOT to do

- No adding features beyond the v1 four without the owner's say-so.
- No third-party analytics or tracking on a teen-facing app without approval.
- No breaking offline Bible access.
- No design drift toward a juvenile or single-gender look.

---

## Legal note (open item)

The owner is checking Kindling with a lawyer before rollout. **Treat launch as
gated on that legal review.** Don't wire up app-store submission, public sign-up,
or anything that constitutes "going live" until that clears.

---

## Related projects (context only, separate repos)

- **Genesis / Loaves, Lamps & Ledgers** — Christian stewardship apps, separate
  build. Nearly ready to roll out after churchgoer testing. Not Kindling; don't
  merge them.
- **Camp Med Manager** — separate repo, separate product.
