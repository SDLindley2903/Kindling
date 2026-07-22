# KINDLING — BUILD COPY DECK v1

**Voice rules for every string in this app:** Write like a good youth pastor talks, not like an adult imitating a teen. No slang that will age in six months. No "yo," no "fam," no exclamation points stacked three deep. Short sentences. Real words. Respect the reader's intelligence. If a line would make a 16-year-old wince, cut it.

**Translation rule:** KJV everywhere. Public domain, zero licensing cost, already bundled from the Genesis refactor. No NIV, no NLT, no exceptions.

## 1. NAME AND TAGLINE

**App name:** Kindling

**Tagline (replaces "Find Out Who You Really Are"):** Small sparks. Real fire.

**Alternate, if you want the promise more explicit:** One card a day. Watch what catches.

**Why the change:** "Find Out Who You Really Are" is a fine line attached to the wrong name. Kindling is about fire. The tagline should be too. Name and promise need to pull the same direction.

**App Store subtitle (30 char limit):** Daily Scripture cards for teens

**Verse lockup (splash screen, about page, marketing):**
*"Did not our heart burn within us, while he talked with us by the way?"* — Luke 24:32

## 2. ONBOARDING (4 screens)

**Screen 1** — Headline: Welcome to Kindling · Sub: Small sparks. Real fire. · Body: One card a day. Thirty seconds. Scripture that actually lands on the life you're living right now.

**Screen 2** — Headline: A card a day · Body: Verse on the front. Real talk on the back. A prayer you can actually pray. Then get on with your day.

**Screen 3** — Headline: Log your hours · Body: Church, community, mission trips. Track the time you serve so it's ready when scholarship applications ask. No more scrambling in April for hours you did in September.

**Screen 4** — Headline: Keep the fire going · Body: Show up, build a streak, share a card with a friend. Miss a day? Just come back. No guilt here. · CTA: Start

## 3. HOME SCREEN

**Greeting line** — time-aware + first name once known:
- Morning: Morning, {name}.
- Afternoon: Afternoon, {name}.
- Evening: Evening, {name}.
- No name yet: Welcome back.

**Under-greeting line (rotates daily, KJV):** *"Let no man despise thy youth."* — 1 Timothy 4:12

**Sign-in prompt:** Sign in to save your streak and your hours

**Today's card block** — Section label: TODAY'S CARD (replaces "SCRIPTURE OF THE DAY") · Secondary action: Open in Bible (replaces "Read in Bible"). Card content pulls from the 31-card set. Day 1 example: *"I will praise thee; for I am fearfully and wonderfully made: marvellous are thy works; and that my soul knoweth right well."* — Psalm 139:14

**Challenges block** — Section label: TODAY'S THREE · Progress: {n} of 3 done
- Read today's card (auto-checks when they flip it)
- Pray for one person by name
- Say one true thing to someone who needs it

*Note: "Read 10 min" is a wall for a kid who doesn't read. "Encourage a friend today" is vague enough to skip. Make the ask small and concrete and they'll actually do it.*

## 4. FEATURE SHELF

Section label: Explore Kindling

**KEEP — four tiles, v1:**

| Tile | Label | Sub-label |
| --- | --- | --- |
| 1 | Cards | 31 days of real talk |
| 2 | Bible | Read the whole thing, offline |
| 3 | Prayer Journal | Write it down. Watch it get answered. |
| 4 | Serve Time | Log hours for scholarships |

*Renamed "Life Cards" to "Cards." Shorter, and "life" was doing no work.*

**CUT — remove from v1:** My Money · Giving · "Presented by Loaves, Lamps & Ledgers" footer
*Reason: a sophomore has no ledger. Money and giving already have a home in Genesis, where the adults are. Kindling stays narrow.*

**DEFER — build later, not for launch:** AI Faith Mentor
*Reason: unsupervised AI chat with 13-year-olds is a moderation and app-review conversation you don't want standing between you and launch day. Ship the four, prove the pilot, then decide.*

## 5. SERVE TIME (the sleeper feature)

This is the one no competitor has. Build it like it matters.

**Empty state** — Headline: No hours logged yet · Body: Serve at church, in your community, on a mission trip? Log it here. When scholarship applications ask for your hours, you'll have the whole record ready instead of guessing. · CTA: Log first hours

**Log entry fields**
- Where (free text: church, food bank, mission trip, coach's clinic)
- Date
- Hours
- What you did (one line, optional)
- Verified by (name + email, optional — this is what makes it count)

**Summary header:** {total} hours logged · {year} total: {n}

**Export button** — Label: Export hours · Sub: PDF summary for scholarship and NHS applications

*Note: the export is the whole point. A logged hour a teen can't prove is a logged hour that doesn't help. Verified-by plus a clean PDF is what turns this from a diary into an asset. This is also the feature that gets a parent to install the app on their kid's phone, which is your real distribution channel.*

## 6. CARD BACK COPY

Field labels on the flip side:
- REAL TALK — two sentences, plain English, connects verse to an actual teen moment
- SPARK — one prayer prompt, starts with an action word, prayable in ten seconds
- Share button: Send this to someone

## 7. STREAK AND NOTIFICATION

**Streak label:** {n} day streak with the flame icon. Grows, never shames.

**Broken streak copy:** Streak reset. Start a new one today.
*Never: "You lost your streak!" Never a guilt trip. Teens delete apps that nag them.*

**Daily notification (one per day, user-picked time):**
- Today's card is up.
- Thirty seconds. Today's card.
- Card's ready when you are.

*Rotate. Never more than one a day. Never worded like a parent.*

## 8. SHARE CARD RENDER

The growth engine. Highest-leverage build item after the cards themselves. Renders card front as a clean image, sized for texting and stories:
- Verse text, large
- Reference
- Small Kindling wordmark, bottom corner, unobtrusive
- No URL slapped across it, no watermark spam

*A teen sending a card to a teen is distribution no ministry budget can buy. Every share is an install ask from a trusted friend instead of an ad.*

## 9. WHAT V1 IS

Four things: **Cards. Bible. Prayer Journal. Serve Time.**

Four things done clean is a product. Nine things done halfway is a hobby. Ship the four, run the pilot at your home church, get the testimonial, then let real teens tell you what number five should be.

## 10. THIS WEEK'S CHECKLIST

- Rip out NIV, drop in the KJV bundle from Genesis
- Pull My Money, Giving, and the Loaves/Lamps/Ledgers footer
- Wire the 31 cards into the Cards tile
- Update home + onboarding copy from this deck
- Register domain, lock social handles
- Reserve "Kindling" in App Store Connect and Google Play Console
- Hand your sophomore the phone and say nothing. Watch where his thumb goes.
