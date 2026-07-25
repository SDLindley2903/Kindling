#!/usr/bin/env python3
"""
Packs Kindling into ONE file (Kindling.html) that opens with a double-click.
It takes the app page and tucks all the card data inside it, so it needs
no server and no internet. Same food, takeout box.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PAGE = os.path.join(ROOT, "app", "static", "index.html")
DATA = os.path.join(ROOT, "data", "topics.json")
OUT = os.path.join(os.path.dirname(ROOT), "Kindling.html")

with open(PAGE, encoding="utf-8") as f:
    html = f.read()
with open(DATA, encoding="utf-8") as f:
    data = json.load(f)

# Safely embed the JSON inside a <script> tag.
blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
inject = "<script>window.KINDLING_DATA = " + blob + ";</script>\n<script>"
html = html.replace("<script>", inject, 1)

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Wrote {OUT} ({os.path.getsize(OUT)/1024:.0f} KB). Double-click it and Kindling opens.")
