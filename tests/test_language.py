"""
The language guard: Kindling speaks to every teen the same.

Our own words (intros, meanings, questions, next steps, taglines) must stay
gender neutral toward the reader. Scripture quotes are exempt on purpose:
we never edit the Bible's text. This test scans only OUR copy, so any future
card that drifts gets caught before it ever ships.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GENDERED = re.compile(
    r"\b(man|men|woman|women|boy|boys|girl|girls|guy|guys|dude|dudes|"
    r"bro|bros|lady|ladies|gentleman|gentlemen|brother|brothers|sister|"
    r"sisters|himself|herself|son|sons|daughter|daughters)\b",
    re.IGNORECASE,
)

# Words we consciously allow, reviewed by a human (Shandy + Dawn).
# "father and mother" / "parents" describe the family, not the reader.
ALLOWED_PHRASES = [
    "father and mother",   # quoting the fifth commandment's language
]


def our_copy_fields(topic):
    fields = [topic["title"], topic["tagline"], topic["intro"],
              topic["meaning"], topic["next_step"]]
    fields += topic["questions"]
    if topic.get("care_note"):
        fields.append(topic["care_note"])
    return fields


def test_our_words_are_gender_neutral():
    with open(os.path.join(ROOT, "data", "topics.json"), encoding="utf-8") as f:
        data = json.load(f)
    problems = []
    for t in data["topics"]:
        for field in our_copy_fields(t):
            scrubbed = field
            for phrase in ALLOWED_PHRASES:
                scrubbed = re.sub(phrase, "", scrubbed, flags=re.IGNORECASE)
            for m in GENDERED.finditer(scrubbed):
                problems.append(f"{t['id']}: '{m.group()}' in: ...{scrubbed[max(0, m.start()-30):m.end()+30]}...")
    assert not problems, "Gendered wording found in our copy:\n" + "\n".join(problems)


def test_app_shell_is_gender_neutral():
    """The UI's own labels and hints, minus any Scripture, stay neutral too."""
    with open(os.path.join(ROOT, "app", "static", "index.html"), encoding="utf-8") as f:
        html = f.read()
    # Strip code; check only human-visible strings in markup and JS literals.
    for m in GENDERED.finditer(html):
        word = m.group().lower()
        # 'man' inside identifiers like 'Romans' is already excluded by \b.
        raise AssertionError(f"Gendered word '{word}' found in the app shell near: "
                             f"...{html[max(0, m.start()-40):m.end()+40]}...")
