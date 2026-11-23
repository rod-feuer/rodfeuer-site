#!/usr/bin/env python3
"""Rebuild the site from the article page published at claude.ai.
Run:  python3 build.py   (reads ../ai-theses-handoff/reports/where-the-ai-money-goes.html)
Writes where-the-ai-money-goes/index.html. index.html, og.png, robots.txt and sitemap.xml are hand-kept.
"""
from pathlib import Path
SRC = Path(__file__).resolve().parent.parent / "ai-theses-handoff" / "reports" / "where-the-ai-money-goes.html"
OUT = Path(__file__).resolve().parent / "where-the-ai-money-goes" / "index.html"
SITE = "https://rodfeuer.com"
TITLE = "Where the AI money goes"
DESC = "597 AI deals and $357B across six VC firms: where strategy says durable profit goes, and where the dollars went."
src = SRC.read_text(encoding="utf-8")
src = src.replace('<title>Where the AI Money Goes</title>', f'<title>{TITLE}</title>', 1)
src = src.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '', 1)
head_meta = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="{DESC}">
<link rel="canonical" href="{SITE}/where-the-ai-money-goes/">
<meta property="og:type" content="article">
<meta property="og:title" content="{TITLE}">
<meta property="og:description" content="{DESC}">
<meta property="og:url" content="{SITE}/where-the-ai-money-goes/">
<meta property="og:image" content="{SITE}/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{TITLE}">
<meta name="twitter:description" content="{DESC}">
<meta name="twitter:image" content="{SITE}/og.png">
<style>:root{{color-scheme:light}}body{{margin:0;font:14px system-ui,sans-serif}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
'''
cut = src.index("</style>") + len("</style>")
out = head_meta + src[:cut] + "\n</head>\n<body>\n" + src[cut:] + "\n</body>\n</html>\n"
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(out, encoding="utf-8")
print("wrote", OUT, len(out), "bytes")
