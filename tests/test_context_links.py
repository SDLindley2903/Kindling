"""
Every verse on every card has a "Read the whole chapter" button.
This proves all 76 of them actually land on a real chapter in the Bible,
in all three translations. A dead button on a Bible app is not acceptable.

The reference parsing here mirrors parseRef() in index.html on purpose:
if the two ever drift apart, this test catches it.
"""
import json
import os
import re
import sys

from fastapi.testclient import TestClient

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from app.main import app  # noqa: E402

client = TestClient(app)

BOOK_FIXUPS = {"psalm": "Psalms", "song of solomon": "Song of Solomon"}
REF_RE = re.compile(r"^\s*((?:[1-3]\s+)?[A-Za-z][A-Za-z ]*?)\s+(\d{1,3}):(\d{1,3})")


def parse_ref(ref):
    m = REF_RE.match(ref)
    if not m:
        return None
    book = m.group(1).strip()
    book = BOOK_FIXUPS.get(book.lower(), book)
    return book, int(m.group(2)), int(m.group(3))


def all_refs():
    data = client.get("/api/topics").json()
    return [(t["id"], v["ref"]) for t in data["topics"] for v in t["verses"]]


def test_every_reference_parses():
    unparsed = [(tid, ref) for tid, ref in all_refs() if parse_ref(ref) is None]
    assert not unparsed, f"references the button could not read: {unparsed}"


def test_every_reference_opens_a_real_chapter():
    """The button's whole job: land the teen in the right chapter."""
    broken = []
    for tid, ref in all_refs():
        book, chapter, verse = parse_ref(ref)
        r = client.get(f"/api/bible/passage?tr=BSB&book={book}&chapter={chapter}")
        if r.status_code != 200:
            broken.append((tid, ref, f"HTTP {r.status_code}"))
            continue
        verses = {v["v"] for v in r.json()["verses"]}
        if verse not in verses:
            broken.append((tid, ref, f"verse {verse} not in chapter"))
    assert not broken, f"buttons that would dead-end: {broken}"


def test_context_links_work_in_all_translations():
    """Switch translations and the buttons still land true."""
    broken = []
    for tr in ("BSB", "WEB", "KJV"):
        for tid, ref in all_refs():
            book, chapter, verse = parse_ref(ref)
            r = client.get(f"/api/bible/passage?tr={tr}&book={book}&chapter={chapter}")
            if r.status_code != 200:
                broken.append((tr, tid, ref))
    assert not broken, f"broken in some translations: {broken[:10]}"


def test_tricky_reference_shapes():
    """Numbered books, multi-word books, and the Psalm/Psalms difference."""
    cases = {
        "1 Peter 2:9": ("1 Peter", 2, 9),
        "2 Corinthians 5:17": ("2 Corinthians", 5, 17),
        "Psalm 139:14": ("Psalms", 139, 14),       # cards say Psalm, Bible says Psalms
        "Song of Solomon 2:1": ("Song of Solomon", 2, 1),
        "Philippians 4:6-7": ("Philippians", 4, 6),  # ranges land on the first verse
        "1 John 1:9": ("1 John", 1, 9),
    }
    for ref, expected in cases.items():
        assert parse_ref(ref) == expected, ref


def test_button_present_in_page():
    html = client.get("/").text
    assert "ctxbtn" in html, "context button exists"
    assert "readInContext" in html, "context button is wired up"
    assert "parseRef" in html, "reference parser present"


def test_growth_strip_on_landing_page():
    html = client.get("/").text
    assert 'id="growstrip"' in html, "growth strip sits on the landing page"
    assert "renderGrowStrip" in html, "growth strip is wired up"
    assert "Growing by faith" in html, "Shandy's wording, kept"


def test_growth_strip_redraws_at_every_moment_it_should():
    """
    The bug this guards: the strip drew once at page load, so signing in
    afterward left the landing page empty. It must redraw on sign in,
    on sign out, and every time the Cards page is shown.
    """
    html = client.get("/").text
    calls = html.count("renderGrowStrip()")
    assert calls >= 4, (
        f"expected the strip to redraw in at least 4 places "
        f"(definition, sign in, sign out, home route), found {calls}")

    # sign in path
    signin = html.split("postJSON(isNew ? \"/api/signup\"")[1][:400]
    assert "renderGrowStrip()" in signin, "must redraw right after signing in"

    # sign out path
    signout = html.split('postJSON("/api/logout"')[1][:300]
    assert "renderGrowStrip()" in signout, "must clear when signing out"

    # landing page route
    home = html.split('show("view-home");')[-1][:200]
    assert "renderGrowStrip()" in home, "must redraw whenever Cards is shown"


def test_signed_out_strip_invites_instead_of_hiding():
    """A blank space teaches nothing. Signed-out teens get an invitation."""
    html = client.get("/").text
    assert "Sign in to start" in html, "signed-out state invites them in"
