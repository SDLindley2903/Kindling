#!/usr/bin/env python3
"""
Kindling content builder.
Reads real Bible text (BSB + KJV from scrollmapper, WEB from TehShrike),
pairs it with our hand-written devotional content, and writes data/topics.json.
Scripture text is always copied from the source files, never typed from memory.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BSB_PATH = os.environ.get("BSB_PATH", "/tmp/BSB.json")
KJV_PATH = os.environ.get("KJV_PATH", "/tmp/KJV.json")
WEB_DIR = os.environ.get("WEB_DIR", "/tmp/world-english-bible/json")
OUT_PATH = os.path.join(ROOT, "data", "topics.json")

# ---------------------------------------------------------------- helpers

def norm_book(name: str) -> str:
    """Normalize book names so 'I Peter', '1 Peter', '1peter' all match."""
    n = name.strip().lower()
    n = re.sub(r"^iii\s+", "3 ", n)
    n = re.sub(r"^ii\s+", "2 ", n)
    n = re.sub(r"^i\s+", "1 ", n)
    n = re.sub(r"[^a-z0-9]", "", n)
    if n == "psalm":
        n = "psalms"
    return n

def load_scrollmapper(path: str) -> dict:
    """-> {norm_book: {chapter: {verse: text}}}"""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    out = {}
    for book in data["books"]:
        chapters = {}
        for ch in book["chapters"]:
            chapters[ch["chapter"]] = {v["verse"]: v["text"].strip() for v in ch["verses"]}
        out[norm_book(book["name"])] = chapters
    return out

# TehShrike WEB: one JSON per book, list of typed nodes
WEB_FILES = {
    "genesis": "genesis", "deuteronomy": "deuteronomy", "joshua": "joshua",
    "psalms": "psalms", "proverbs": "proverbs", "ecclesiastes": "ecclesiastes",
    "isaiah": "isaiah", "jeremiah": "jeremiah", "matthew": "matthew",
    "john": "john", "romans": "romans", "1corinthians": "1corinthians",
    "2corinthians": "2corinthians", "galatians": "galatians",
    "ephesians": "ephesians", "philippians": "philippians",
    "colossians": "colossians", "2timothy": "2timothy", "hebrews": "hebrews",
    "james": "james", "1peter": "1peter", "exodus": "exodus",
    "1samuel": "1samuel", "zephaniah": "zephaniah", "1john": "1john",
}

def load_web_book(book_norm: str) -> dict:
    """-> {chapter: {verse: text}} for one WEB book."""
    fname = WEB_FILES[book_norm] + ".json"
    with open(os.path.join(WEB_DIR, fname), encoding="utf-8") as f:
        nodes = json.load(f)
    chapters = {}
    for node in nodes:
        if "text" not in node.get("type", ""):
            continue
        ch = node.get("chapterNumber")
        vs = node.get("verseNumber")
        val = node.get("value", "")
        if ch is None or vs is None or not val:
            continue
        chapters.setdefault(ch, {}).setdefault(vs, []).append(val)
    return {ch: {v: re.sub(r"\s+", " ", "".join(parts)).strip() for v, parts in verses.items()}
            for ch, verses in chapters.items()}

def get_text(source: dict, book_norm: str, chapter: int, verses: list) -> str:
    chap = source[book_norm][chapter]
    return " ".join(chap[v] for v in verses).strip()

# ---------------------------------------------------------------- content
# Verse references are the recipe. Text is fetched from the real Bibles.
# Devotional words below are ours, for Shandy and Dawn to review.

def V(ref, book, chapter, *verses):
    return {"ref": ref, "book": book, "chapter": chapter, "verses": list(verses)}

CARDS = [
    {
        "id": "identity",
        "title": "Identity",
        "tagline": "Who does God say I am?",
        "emoji": "\U0001FA9E",
        "heavy": False,
        "intro": "Everyone has a voice in their head asking, who am I really? Grades, sports, followers, and friends all try to answer it for you. God already did.",
        "meaning": "You are not an accident, and you are not your worst day. The God who made galaxies made you on purpose, in His image, and He calls you His child. Labels from school or a screen can change in a week. What God says about you does not move. When you build who you are on what He says, you stop chasing proof that you matter. You already have it.",
        "verse_refs": [
            V("Genesis 1:27", "Genesis", 1, 27),
            V("Psalm 139:14", "Psalms", 139, 14),
            V("John 1:12", "John", 1, 12),
            V("2 Corinthians 5:17", "2 Corinthians", 5, 17),
            V("Galatians 2:20", "Galatians", 2, 20),
            V("Ephesians 2:10", "Ephesians", 2, 10),
            V("1 Peter 2:9", "1 Peter", 2, 9),
        ],
        "questions": [
            "Which label do you wear most at school, and who gave it to you?",
            "Read Psalm 139:14 again. What changes if you really believe God made you wonderfully, on purpose?",
            "What is the difference between what you do and who you are?",
        ],
        "next_step": "Tonight, write down one lie you believe about yourself. Next to it, write one of these verses that answers it. Keep it where you will see it tomorrow.",
    },
    {
        "id": "anxiety",
        "title": "Anxiety & Worry",
        "tagline": "When my mind won't slow down",
        "emoji": "\U0001F30A",
        "heavy": True,
        "intro": "Racing thoughts before a test. That knot in your stomach at night. Worry is loud, and it lies about tomorrow. God offers a trade: your anxiety for His peace.",
        "meaning": "God never says pretend everything is fine. He says bring it to Me, all of it, in prayer. Casting your cares on Him is not weakness, it is trust. His peace does not always change the situation first. It guards your heart and mind while He works. And He asks you to live one day at a time, because tomorrow's worries are not yours to carry today.",
        "verse_refs": [
            V("Philippians 4:6-7", "Philippians", 4, 6, 7),
            V("1 Peter 5:7", "1 Peter", 5, 7),
            V("Matthew 6:34", "Matthew", 6, 34),
            V("Isaiah 41:10", "Isaiah", 41, 10),
            V("Psalm 94:19", "Psalms", 94, 19),
            V("John 14:27", "John", 14, 27),
        ],
        "questions": [
            "What is one worry you have carried this week that you have never actually prayed about?",
            "Philippians 4:6-7 says to pray with thanksgiving. Why do you think thankfulness helps quiet worry?",
            "What would it look like to hand God one worry each night before bed?",
        ],
        "next_step": "Try the trade tonight: say one worry out loud to God, thank Him for one thing, and leave both with Him.",
    },
    {
        "id": "depression",
        "title": "Depression & Sadness",
        "tagline": "When everything feels gray",
        "emoji": "\U0001F305",
        "heavy": True,
        "intro": "Some days are heavier than words. If that is you, hear this first: God is not disappointed in you, and you are not alone in the dark. He stays close to crushed hearts.",
        "meaning": "The Bible is full of people who felt exactly this. David asked his own soul, why are you so downcast? Jesus wept. God does not rush your sadness or shame you for it. He stays close to the brokenhearted, and He promises the night does not get the last word. Joy comes in the morning is not a quick fix. It is a promise from Someone who never breaks one. Keep walking, keep talking to Him, and let people love you through it.",
        "verse_refs": [
            V("Psalm 34:18", "Psalms", 34, 18),
            V("Psalm 42:11", "Psalms", 42, 11),
            V("Matthew 11:28", "Matthew", 11, 28),
            V("Isaiah 43:2", "Isaiah", 43, 2),
            V("Psalm 30:5", "Psalms", 30, 5),
            V("Romans 8:38-39", "Romans", 8, 38, 39),
        ],
        "questions": [
            "Psalm 34:18 says God is close to the brokenhearted. Have you ever felt that closeness? What was it like?",
            "David talked to his own soul in Psalm 42:11. What would you say to yours?",
            "Who is one safe person God has put in your life for the heavy days?",
        ],
        "next_step": "Tell one trusted person how you are really doing this week. Not the fine version. The real one.",
    },
    {
        "id": "loneliness",
        "title": "Loneliness",
        "tagline": "When I feel invisible",
        "emoji": "\U0001F56F",
        "heavy": True,
        "intro": "You can be in a crowded hallway and still feel completely alone. Loneliness tells you nobody sees you. God answers by name: I see you, I am with you, and I am not leaving.",
        "meaning": "Never will I leave you is one of the strongest promises in the whole Bible. God also builds lonely people into families, through friends, church, and people who become home. Feeling alone is real, but being alone is not your truth. The God who calls you by name stays.",
        "verse_refs": [
            V("Deuteronomy 31:6", "Deuteronomy", 31, 6),
            V("Psalm 68:6", "Psalms", 68, 6),
            V("Psalm 23:4", "Psalms", 23, 4),
            V("Matthew 28:20", "Matthew", 28, 20),
            V("Hebrews 13:5", "Hebrews", 13, 5),
            V("John 14:18", "John", 14, 18),
            V("Isaiah 43:1", "Isaiah", 43, 1),
        ],
        "questions": [
            "When do you feel loneliness the most: at school, online, or at home? Why there?",
            "God promises He will never leave. Why is that hard to feel some days?",
            "Who around you might be lonelier than they look? What could you do about it this week?",
        ],
        "next_step": "Do for someone else what you wish someone would do for you: send the first text. Invite one person in.",
    },
    {
        "id": "fear",
        "title": "Fear & Courage",
        "tagline": "Doing it scared",
        "emoji": "\U0001F981",
        "heavy": False,
        "intro": "Courage is not the absence of fear. It is trusting God while your knees shake. Joshua heard it straight: be strong and courageous, for the Lord your God is with you wherever you go.",
        "meaning": "God's answer to fear is not try harder. It is I am with you. Again and again the Bible says do not fear, and almost every time the reason is the same: because I am with you. David wrote, when I am afraid, I will trust in You. Not if I am afraid. When. Fear will show up. Courage is choosing to move anyway, with God beside you, and finding out He was holding your hand the whole time.",
        "verse_refs": [
            V("Joshua 1:9", "Joshua", 1, 9),
            V("2 Timothy 1:7", "2 Timothy", 1, 7),
            V("Psalm 56:3", "Psalms", 56, 3),
            V("Psalm 27:1", "Psalms", 27, 1),
            V("Isaiah 41:13", "Isaiah", 41, 13),
            V("Romans 8:31", "Romans", 8, 31),
            V("Psalm 118:6", "Psalms", 118, 6),
        ],
        "questions": [
            "What is something God might want you to do that fear keeps talking you out of?",
            "Psalm 56:3 says when I am afraid, not if. Why does that one word matter?",
            "Where have you already seen God come through when you were scared?",
        ],
        "next_step": "Name your biggest fear out loud to God. Then take one small brave step toward the thing this week, scared and all.",
    },
    {
        "id": "anger",
        "title": "Anger",
        "tagline": "Before I blow up",
        "emoji": "\U0001F30B",
        "heavy": False,
        "intro": "Anger itself is not the sin. It is what anger does with you, and what you do with it, that matters. God offers a better way than blowing up or bottling up.",
        "meaning": "Be quick to listen, slow to speak, slow to anger. That order is the whole playbook. Anger usually wants to talk first, but wise people flip it. A gentle answer really does turn away wrath, at home, in the group chat, everywhere. And do not let the sun go down on your anger means deal with it fast, before it hardens into something that owns you. Fools vent everything. The wise bring it to God first and let Him cool the coals.",
        "verse_refs": [
            V("Ephesians 4:26", "Ephesians", 4, 26),
            V("James 1:19-20", "James", 1, 19, 20),
            V("Proverbs 15:1", "Proverbs", 15, 1),
            V("Proverbs 29:11", "Proverbs", 29, 11),
            V("Psalm 37:8", "Psalms", 37, 8),
            V("Colossians 3:8", "Colossians", 3, 8),
        ],
        "questions": [
            "What flips your switch fastest? What is usually underneath that anger: hurt, embarrassment, unfairness?",
            "Quick to listen, slow to speak. Which half is harder for you?",
            "Is there any anger you have carried past sundown that God wants you to put down?",
        ],
        "next_step": "Next time heat rises, try the 3-count: pause, one slow breath, one silent prayer. Then speak.",
    },
    {
        "id": "friendship",
        "title": "Friendship & Peer Pressure",
        "tagline": "Choosing my people",
        "emoji": "\U0001F91D",
        "heavy": False,
        "intro": "Who you walk with shapes who you become, so God talks a lot about choosing your people wisely and being the friend worth having.",
        "meaning": "Walk with the wise and become wise. Bad company really does corrupt good character, not because you are weak, but because everyone becomes like their crowd eventually. That is how God built us. So this is not about being better than anyone. It is about direction: are your closest people pulling you toward God or away from Him? And flip it around: iron sharpens iron. Be the friend who makes the people around you braver, kinder, and closer to Jesus.",
        "verse_refs": [
            V("Proverbs 13:20", "Proverbs", 13, 20),
            V("1 Corinthians 15:33", "1 Corinthians", 15, 33),
            V("Proverbs 17:17", "Proverbs", 17, 17),
            V("Ecclesiastes 4:9-10", "Ecclesiastes", 4, 9, 10),
            V("Romans 12:2", "Romans", 12, 2),
            V("Proverbs 27:17", "Proverbs", 27, 17),
        ],
        "questions": [
            "Think of your three closest friends. Which direction are they pulling you?",
            "Where do you feel pressure to shrink your faith to fit in?",
            "Iron sharpens iron. Who do you sharpen, and who sharpens you?",
        ],
        "next_step": "Ask God for one friendship that points you toward Him. Then be that friend for somebody else this week.",
    },
    {
        "id": "purpose",
        "title": "Purpose & My Future",
        "tagline": "What am I here for?",
        "emoji": "\U0001F9ED",
        "heavy": False,
        "intro": "College, career, who to become: the future can feel like a fog. Good news: God is not nervous about your future. He wrote plans for you before you had a name.",
        "meaning": "I know the plans I have for you, plans to give you hope and a future. God said that to people walking through a hard season, which means His plans hold even when life does not look like the dream. Your job is not to see the whole map. It is to trust Him with the next step. Lean not on your own understanding means you do not have to have it all figured out at fifteen, or fifty. Walk with Him, work with your whole heart right where you are, and He will keep making your path straight, one step at a time.",
        "verse_refs": [
            V("Jeremiah 29:11", "Jeremiah", 29, 11),
            V("Proverbs 3:5-6", "Proverbs", 3, 5, 6),
            V("Romans 8:28", "Romans", 8, 28),
            V("Psalm 32:8", "Psalms", 32, 8),
            V("Philippians 1:6", "Philippians", 1, 6),
            V("Colossians 3:23", "Colossians", 3, 23),
        ],
        "questions": [
            "What about the future stresses you most? What would trusting God with just that piece look like?",
            "Proverbs 3:5-6 says lean not on your own understanding. Where are you leaning hardest on your own plan?",
            "What has God put in your hands right now, today, that you could do with your whole heart?",
        ],
        "next_step": "Stop asking what is the whole plan and ask what is the next step. Write down one faithful thing you can do this month.",
    },
    {
        "id": "forgiveness",
        "title": "Forgiveness",
        "tagline": "Letting it go, getting it back",
        "emoji": "\U0001F54A️",
        "heavy": False,
        "intro": "Somebody hurt you, or you are the one who blew it. Either way, forgiveness feels impossible some days. God is an expert at it, giving it and helping you give it.",
        "meaning": "Forgive as God forgave you. That is the engine of the whole thing. You do not forgive because the hurt was small. You forgive because you have been forgiven much, and because unforgiveness is a backpack full of bricks God never asked you to carry. And when you are the one who messed up: confess it. He is faithful to forgive, and He moves your sin as far away as east is from west. Peter asked how many times to forgive. Jesus answered with a number so big it stops being math and becomes a way of life.",
        "verse_refs": [
            V("Ephesians 4:32", "Ephesians", 4, 32),
            V("Colossians 3:13", "Colossians", 3, 13),
            V("Matthew 6:14", "Matthew", 6, 14),
            V("1 John 1:9", "1 John", 1, 9),
            V("Psalm 103:12", "Psalms", 103, 12),
            V("Matthew 18:21-22", "Matthew", 18, 21, 22),
        ],
        "questions": [
            "Who is heaviest to think about right now? What would handing that hurt to God look like?",
            "Matthew 6:14 connects receiving forgiveness with giving it. Why do you think those travel together?",
            "Is there something you need to confess and finally let God carry?",
        ],
        "next_step": "Write one name, maybe even your own. Pray one sentence: God, help me release this. Repeat tomorrow.",
    },
    {
        "id": "selfworth",
        "title": "Self-Worth & Body Image",
        "tagline": "More than a mirror",
        "emoji": "\U0001F331",
        "heavy": True,
        "intro": "Mirrors and phones both lie about your worth. God does not measure you in likes, sizes, or streaks. Hear what the One who made you says.",
        "meaning": "People look at the outside. God looks at the heart. He knit you together before anyone had an opinion about you, and He says you are precious and honored in His eyes. Your body is not a project to fix for an audience. It is a gift to care for, a temple where God is glad to live. Sparrows sell cheap, and God does not miss a single one. You are worth more than many sparrows, on your best day and on your worst.",
        "verse_refs": [
            V("Psalm 139:13-14", "Psalms", 139, 13, 14),
            V("1 Samuel 16:7", "1 Samuel", 16, 7),
            V("Matthew 10:29-31", "Matthew", 10, 29, 30, 31),
            V("Isaiah 43:4", "Isaiah", 43, 4),
            V("1 Corinthians 6:19-20", "1 Corinthians", 6, 19, 20),
            V("Zephaniah 3:17", "Zephaniah", 3, 17),
        ],
        "questions": [
            "Where do you go looking for proof that you are enough: mirrors, likes, grades, wins?",
            "1 Samuel 16:7 says God looks at the heart. How would this week change if you believed that?",
            "What is one way you can care for your body this week like it is a gift, not a project?",
        ],
        "next_step": "Unfollow one account that makes you feel small. Read Psalm 139 before bed instead.",
    },
    {
        "id": "family",
        "title": "Family",
        "tagline": "Under my roof",
        "emoji": "\U0001F3E0",
        "heavy": True,
        "intro": "Family can be your softest place or your hardest test, sometimes both in the same dinner. God lives in the middle of real families, not perfect ones.",
        "meaning": "Honor your father and mother is the first command with a promise attached. Honor does not mean your family is perfect, and it does not mean pretending. It means treating the people under your roof with the same patience and grace God keeps giving you: bearing with one another, quick to forgive, slow to slam doors. How good it is when a family lives in unity. Not easy. Good. And if home is a hard place right now, God sees you, God stays with you, and He puts safe people around you who can help.",
        "verse_refs": [
            V("Exodus 20:12", "Exodus", 20, 12),
            V("Ephesians 6:1-3", "Ephesians", 6, 1, 2, 3),
            V("Ephesians 4:2-3", "Ephesians", 4, 2, 3),
            V("Psalm 133:1", "Psalms", 133, 1),
            V("1 John 4:19", "1 John", 4, 19),
            V("Proverbs 17:6", "Proverbs", 17, 6),
        ],
        "questions": [
            "What is one way you could honor your parents this week that would actually surprise them?",
            "Ephesians 4:2 talks about bearing with one another in love. Who in your family needs the most patience from you, and why?",
            "What do you want your family to feel like, and what is one thing you can do to help build that?",
        ],
        "next_step": "Do one unasked chore this week. Say one thank you out loud at dinner. Watch what happens.",
    },
    {
        "id": "temptation",
        "title": "Temptation",
        "tagline": "When the pull is strong",
        "emoji": "\U0001F9F2",
        "heavy": False,
        "intro": "Everybody gets pulled. Even Jesus was tempted, so He knows exactly how strong the pull feels. The good news: no pull is stronger than the way out God promises.",
        "meaning": "No temptation grabs you that is not common to everyone, and God is faithful. He always builds an exit door. Your job is to look for it and walk through it. Resist the devil and he will flee: temptation loses power when you stop negotiating with it. Hide God's word in your heart, keep praying, and walk with people headed the same direction. And when you fall, grace gets the last word, not shame. Get up, come boldly back to God, and keep walking.",
        "verse_refs": [
            V("1 Corinthians 10:13", "1 Corinthians", 10, 13),
            V("James 4:7", "James", 4, 7),
            V("Matthew 26:41", "Matthew", 26, 41),
            V("Psalm 119:11", "Psalms", 119, 11),
            V("Hebrews 4:15-16", "Hebrews", 4, 15, 16),
            V("Galatians 5:16", "Galatians", 5, 16),
            V("2 Timothy 2:22", "2 Timothy", 2, 22),
        ],
        "questions": [
            "Where does the pull hit you hardest: your phone, your words, your habits?",
            "1 Corinthians 10:13 promises a way out. In your strongest temptation, what is usually the exit door?",
            "Who could you text for backup when the pull gets loud?",
        ],
        "next_step": "Name your loudest temptation and its exit door. Set one guardrail this week: an app limit, a new route, a backup friend.",
    },
]

CARE_NOTE = ("If the weight feels too heavy, please do not carry it alone. "
             "Tell a parent, pastor, school counselor, or another adult you trust. "
             "In the US you can call or text 988 (Suicide & Crisis Lifeline) anytime, day or night.")

# ---------------------------------------------------------------- build

def main():
    print("Loading Bibles...")
    bsb = load_scrollmapper(BSB_PATH)
    kjv = load_scrollmapper(KJV_PATH)
    web_cache = {}

    topics = []
    missing = []
    for card in CARDS:
        verses_out = []
        for vr in card["verse_refs"]:
            bnorm = norm_book(vr["book"])
            entry = {"ref": vr["ref"]}
            try:
                entry["BSB"] = get_text(bsb, bnorm, vr["chapter"], vr["verses"])
            except KeyError:
                missing.append(("BSB", vr["ref"], sorted(bsb.keys())[:5]))
                entry["BSB"] = ""
            try:
                entry["KJV"] = get_text(kjv, bnorm, vr["chapter"], vr["verses"])
            except KeyError:
                missing.append(("KJV", vr["ref"], ""))
                entry["KJV"] = ""
            try:
                if bnorm not in web_cache:
                    web_cache[bnorm] = load_web_book(bnorm)
                entry["WEB"] = get_text(web_cache, bnorm, vr["chapter"], vr["verses"])
            except (KeyError, FileNotFoundError) as e:
                missing.append(("WEB", vr["ref"], str(e)))
                entry["WEB"] = ""
            verses_out.append(entry)
        topic = {k: card[k] for k in
                 ("id", "title", "tagline", "emoji", "heavy", "intro", "meaning",
                  "questions", "next_step")}
        topic["verses"] = verses_out
        if card["heavy"]:
            topic["care_note"] = CARE_NOTE
        topics.append(topic)

    payload = {
        "app": "Kindling",
        "tagline": "Light for the fires you're walking through.",
        "translations": {
            "BSB": "Berean Standard Bible",
            "WEB": "World English Bible",
            "KJV": "King James Version",
        },
        "default_translation": "BSB",
        "topics": topics,
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    n_verses = sum(len(t["verses"]) for t in topics)
    print(f"Wrote {OUT_PATH}: {len(topics)} cards, {n_verses} verse entries x 3 translations.")
    if missing:
        print("MISSING TEXT:")
        for m in missing:
            print("  ", m)
        sys.exit(1)
    print("All verse text present in all 3 translations. OK")

if __name__ == "__main__":
    main()
