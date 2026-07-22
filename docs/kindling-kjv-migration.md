# KINDLING — KJV MIGRATION SHEET

## WHY THIS MATTERS (read once, then never worry again)

The NIV is owned property. Biblica holds the copyright, Zondervan and HarperCollins control commercial licensing. Their permission policy allows limited free quotation, but it does not cover an app whose core product **is** the verses. That's a commercial license with fees, an application, and a review of your content. The CSB, NLT, ESV, and NASB all have their own versions of the same gate.

The KJV is public domain in the United States. No application. No fee. No permission letter. No one can revoke it or change the terms on you after you have 5,000 teens using the app.

You already own an offline KJV bundle from the Genesis ownership refactor. It's built, it's tested, and it's sitting right there. Use it.

**Cost to fix today: one afternoon. Cost to fix after launch: a lawyer, a rebuild, and possibly a takedown.**

## PART 1: CONFIRMED NON-KJV STRINGS IN YOUR BUILD

These two are live on the home screen right now.

### Swap 1 — Home screen, under-greeting line

**Currently (not KJV):** "Walk in wisdom, making the most of your time."

**KJV replacement (Colossians 4:5):** "Walk in wisdom toward them that are without, redeeming the time."

**Better move:** this verse is about how you carry yourself toward outsiders. Fine verse, wrong shelf. For a teen home screen, use *"Let no man despise thy youth."* — 1 Timothy 4:12. That one lands on a 15-year-old like a hand on the shoulder.

### Swap 2 — Scripture of the Day block

**Currently (NIV):** "Give, and it will be given to you. A good measure, pressed down, shaken together and running over, will be poured into your lap." — Luke 6:38

**KJV replacement (Luke 6:38):** "Give, and it shall be given unto you; good measure, pressed down, and shaken together, and running over, shall men give into your bosom."

**Better move:** don't swap it, replace it. Luke 6:38 is a giving verse and this is not a giving app. This block should pull from the 31-card set by day of month. On the 1st it should read *"I will praise thee; for I am fearfully and wonderfully made: marvellous are thy works; and that my soul knoweth right well."* — Psalm 139:14.

## PART 2: FIND THE REST YOURSELF (10 minutes)

I could only see the home screen. There are almost certainly more non-KJV strings hiding in onboarding, empty states, and any seeded card content. Here's how to flush them out.

### Grep your repo for modern-translation tells

KJV never uses these words:

```bash
# Modern pronouns and contractions KJV never uses in verse text
grep -rniE "\b(you're|don't|won't|isn't|can't|it's)\b" src/ --include=*.{ts,tsx,js,jsx,json}

# Modern words that signal NIV/CSB/NLT verse text
grep -rniE "\b(opportunity|encourage|attitude|relationship|generous|lap)\b" src/ --include=*.{ts,tsx,js,jsx,json}

# Find every quoted string with a verse reference nearby
grep -rniE "(Psalm|Proverbs|Matthew|Mark|Luke|John|Romans|Corinthians|Galatians|Ephesians|Philippians|Colossians|Thessalonians|Timothy|Hebrews|James|Peter|Joshua|Deuteronomy|Jeremiah) [0-9]+:[0-9]+" src/
```

### The eyeball test

KJV always has these. If a verse string lacks them entirely, it's not KJV:

| KJV says | Modern versions say |
| --- | --- |
| thee, thou, thy, thine, ye | you, your |
| -eth endings (loveth, giveth, saith) | loves, gives, says |
| shall | will |
| unto | to |
| verily | truly |

**Fast rule:** if it reads smooth and modern, it isn't KJV. If it reads a little old and a little heavy, it is.

## PART 3: THE REAL FIX (do this instead of find-and-replace)

Find-and-replace fixes today's strings. It does nothing about the next verse you hardcode at 11pm six weeks from now.

**The architectural fix: stop hardcoding verse text at all.** Cards should carry a **reference only**, and the text should be looked up from the KJV bundle at render.

**Card data becomes:**

```json
{
  "day": 1,
  "theme": "IDENTITY",
  "ref": "PSA.139.14",
  "realTalk": "The mirror and the comment section don't get the final word on you. The One who made you already called the work marvellous.",
  "spark": "Thank God for one thing about how He made you, out loud, right now."
}
```

**Render becomes:**

```js
const verseText = kjv.lookup(card.ref);
```

Three things happen the moment you do this:

1. **A non-KJV verse becomes structurally impossible.** There's nowhere to put one.
2. **"Open in Bible" gets easy.** You already have the reference.
3. **One bundle serves the whole app.** Cards, reader, daily verse, share render.

**Note on Real Talk and Spark:** those are your words, not Scripture. They stay as literals. Copyright only bites on the verse text.

## PART 4: THE 31 CARDS ARE ALREADY KJV

Every verse in `kindling-card-spec-and-31-days.md` is King James, checked and clean. Wire that file in as your card data and your entire card deck is licensed-free from day one.

Four of them (Days 2, 3, 9, 20) are trimmed to the relevant clause for card readability. That's normal and fine, and with reference-based lookup the full verse is one tap away in the reader.

## PART 5: CHECKLIST

- [ ] Swap the home screen under-greeting to 1 Timothy 4:12 (KJV)
- [ ] Replace the Luke 6:38 block with day-of-month lookup from the 31-card set
- [ ] Run the three grep commands above, fix every hit
- [ ] Refactor card data to reference-only (ref field, no verse text)
- [ ] Point the lookup at the KJV bundle from the Genesis repo
- [ ] Add one line to your README: **KJV only. Public domain. Never hardcode verse text.**

## PART 6: WHAT TO TELL THE APP STORES

When you submit, both stores will ask about content rights. Your answer is one clean sentence:

> All Scripture text is King James Version, public domain in the United States. All commentary is original work by the developer.

No paperwork. No waiting on a permissions department. That's the whole reason KJV is worth the thees and thous.
