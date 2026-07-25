#!/usr/bin/env python3
"""
Packs all three complete Bibles into small compressed files the app owns,
so Kindling never depends on anyone else's server for Scripture.
Creates data/bible/BSB.jsonl.gz, KJV.jsonl.gz, WEB.jsonl.gz.
Each line: {"b": book, "o": book_order, "c": chapter, "v": verse, "t": text}
"""
import gzip
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_DIR = os.path.join(ROOT, "data", "bible")
BSB_PATH = os.environ.get("BSB_PATH", "/tmp/BSB.json")
KJV_PATH = os.environ.get("KJV_PATH", "/tmp/KJV.json")
WEB_DIR = os.environ.get("WEB_DIR", "/tmp/world-english-bible/json")


def norm(name: str) -> str:
    n = name.strip().lower()
    n = re.sub(r"^iii\s+", "3 ", n)
    n = re.sub(r"^ii\s+", "2 ", n)
    n = re.sub(r"^i\s+", "1 ", n)
    n = re.sub(r"[^a-z0-9]", "", n)
    return "psalms" if n == "psalm" else n


def pretty(name: str) -> str:
    """Friendly display names: 'III John' -> '3 John', 'Revelation of John' -> 'Revelation'."""
    n = name.strip()
    n = re.sub(r"^III\s+", "3 ", n)
    n = re.sub(r"^II\s+", "2 ", n)
    n = re.sub(r"^I\s+", "1 ", n)
    if n.lower().startswith("revelation"):
        n = "Revelation"
    return n


def write_rows(code: str, rows):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"{code}.jsonl.gz")
    with gzip.open(path, "wt", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{code}: {len(rows):,} verses -> {path} ({os.path.getsize(path)/1024:.0f} KB)")
    return len(rows)


def load_scrollmapper(code: str, path: str):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    rows, canon = [], []
    for order, book in enumerate(data["books"], start=1):
        display = pretty(book["name"])
        canon.append((order, display))
        for ch in book["chapters"]:
            for v in ch["verses"]:
                txt = v["text"].strip()
                if txt:
                    rows.append({"b": display, "o": order,
                                 "c": ch["chapter"], "v": v["verse"], "t": txt})
    write_rows(code, rows)
    return canon


ALIASES = {
    "revelation": ["revelationofjohn", "therevelationofjohn", "revelationofjesuschrist"],
    "songofsolomon": ["songofsongs"],
}


def load_web(canon):
    """TehShrike WEB: one file per book. Match to canonical names/order from BSB."""
    by_norm = {norm(name): (order, name) for order, name in canon}
    for short, longs in ALIASES.items():
        for long in longs:
            if long in by_norm and short not in by_norm:
                by_norm[short] = by_norm[long]
            if short in by_norm and long not in by_norm:
                by_norm[long] = by_norm[short]
    rows, missing = [], []
    for fname in sorted(os.listdir(WEB_DIR)):
        if not fname.endswith(".json"):
            continue
        key = norm(fname[:-5])
        if key not in by_norm:
            missing.append(fname)
            continue
        order, display = by_norm[key]
        with open(os.path.join(WEB_DIR, fname), encoding="utf-8") as f:
            nodes = json.load(f)
        acc = {}
        for node in nodes:
            if "text" not in node.get("type", ""):
                continue
            ch, vs, val = node.get("chapterNumber"), node.get("verseNumber"), node.get("value", "")
            if ch is None or vs is None or not val:
                continue
            acc.setdefault((ch, vs), []).append(val)
        for (ch, vs), parts in sorted(acc.items()):
            txt = re.sub(r"\s+", " ", "".join(parts)).strip()
            if txt:
                rows.append({"b": display, "o": order, "c": ch, "v": vs, "t": txt})
    rows.sort(key=lambda r: (r["o"], r["c"], r["v"]))
    write_rows("WEB", rows)
    if missing:
        print("Unmatched WEB files (skipped):", missing)


def main():
    canon = load_scrollmapper("BSB", BSB_PATH)
    load_scrollmapper("KJV", KJV_PATH)
    load_web(canon)
    print("Pantry packed. The app now owns its own Scripture.")


if __name__ == "__main__":
    sys.exit(main())
