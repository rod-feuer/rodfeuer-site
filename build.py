#!/usr/bin/env python3
"""Rebuild the site from the article page published at claude.ai.
Run:  python3 build.py   (reads ../ai-theses-handoff/reports/where-the-ai-money-goes.html)
Writes where-the-ai-money-goes/index.html. index.html, og.png, robots.txt and sitemap.xml are hand-kept.
"""
import json, re, subprocess, sys
from pathlib import Path
SRC = Path(__file__).resolve().parent.parent / "ai-theses-handoff" / "reports" / "where-the-ai-money-goes.html"
OUT = Path(__file__).resolve().parent / "where-the-ai-money-goes" / "index.html"
SITE = "https://rodfeuer.com"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
LINKEDIN = "https://www.linkedin.com/in/rodfeuer/"
X_PROFILE = "https://x.com/rodfeuer"
PUBLISHED = "2026-11"      # month only: the exact first-publish day is not recorded
MODIFIED = "2026-11-22"
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
person = {"@type": "Person", "name": "Rod Feuer", "url": SITE + "/", "image": SITE + "/headshot.jpg", "description": "Rod Feuer is a product and strategy executive who writes about AI, strategy, and positioning.", "sameAs": [LINKEDIN, X_PROFILE]}
article_ld = {
    "@context": "https://schema.org", "@type": "Article", "headline": TITLE, "description": DESC,
    "author": person, "publisher": person, "inLanguage": "en",
    "datePublished": PUBLISHED, "dateModified": MODIFIED,
    "mainEntityOfPage": SITE + "/where-the-ai-money-goes/", "image": SITE + "/og.png",
}
head_extra = ('<script type="application/ld+json">' + json.dumps(article_ld) + '</script>\n'
  '<style>.byline{font:600 15px/1.3 var(--sans);color:var(--text-secondary);margin:0 0 6px}.byline a{color:inherit}'
  '.keyfacts{background:var(--surface-2);border-radius:8px;padding:16px 20px;margin:20px 0 0;max-width:720px}'
  '.keyfacts h2{font:700 13px/1 var(--sans);letter-spacing:.14em;text-transform:uppercase;color:var(--text-muted);margin:0 0 10px}'
  '.keyfacts ul{margin:0;padding-left:1.1em}.keyfacts li{margin:0 0 8px;font:400 17px/1.45 var(--serif)}</style>\n')
cut = src.index("</style>") + len("</style>")
body = src[cut:]
# byline + machine-readable date, then key findings (all figures are stated in the article)
byline = ('<p class="byline">By <a href="' + SITE + '/" rel="author">Rod Feuer</a> \u00b7 '
          '<time datetime="' + PUBLISHED + '">November 2026</time></p>\n')
keyfacts = (
 '<section class="keyfacts" aria-labelledby="kf"><h2 id="kf">Key findings</h2><ul>'
 "<li>597 AI deals and $357B in round size: every AI round of $5M or more with a public size that six VC firms joined, January 2024 to October 2026.</li>"
 "<li>Agents drew 43% of the deals but 7% of the dollars. Frontier labs drew 3% of the deals and 70% of the dollars; OpenAI's $122B round is about a third of all the dollars.</li>"
 "<li>Systems of record drew about 0.2% of the dollars (19 deals). Compute startups, mostly inference platforms, drew 2.5%.</li>"
 "<li>Strategy predicts durable profit goes to chipmakers, hyperscalers, and systems of record. Two likely reasons so few venture dollars reached them: the incumbents don't raise venture rounds, and few records startups raised rounds at all. The data can't say which matters more.</li>"
 "</ul></section>\n")
m = re.search(r'<p class="dateline">.*?</p>\n', body, flags=re.S)
assert m, "dateline not found"
body = body[:m.start()] + byline + m.group(0) + keyfacts + body[m.end():]
# the one SVG icon without a label is decorative; the routes diagram needs a label
body = body.replace('<svg width="18" height="18" viewBox="0 0 18 18" style="vertical-align:-4px;margin-right:4px">',
                    '<svg width="18" height="18" viewBox="0 0 18 18" style="vertical-align:-4px;margin-right:4px" aria-hidden="true">', 1)
body = body.replace('<svg class="routes" width="100%" viewBox="0 0 793 534" role="img">',
                    '<svg class="routes" width="100%" viewBox="0 0 793 534" role="img" aria-label="Two routes into records and rules: become a new system of record, or become the system of intelligence">', 1)
out = head_meta + src[:cut] + head_extra + "\n</head>\n<body>\n" + body + "\n</body>\n</html>\n"
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(out, encoding="utf-8")
print("wrote", OUT, len(out), "bytes (before pre-render)")

# Pre-render: the charts and 7 of 10 tables are drawn by JavaScript, which many crawlers (including most AI
# crawlers) do not run. Serialize the rendered DOM so the figures and tables are in the static HTML. The script
# stays: it re-draws the same content on load (it assigns innerHTML), so interactivity is unchanged.
r = subprocess.run([CHROME, "--headless", "--disable-gpu", "--virtual-time-budget=8000", "--window-size=1200,900",
                    "--dump-dom", OUT.resolve().as_uri()], capture_output=True, text=True, timeout=120)
dom = r.stdout
if "<table" not in dom or len(dom) < 0.8 * len(out):
    sys.exit("pre-render failed; kept the un-rendered page")
if not dom.lstrip().lower().startswith("<!doctype"):
    dom = "<!doctype html>\n" + dom
OUT.write_text(dom, encoding="utf-8")
static = re.sub(r"<script\b.*?</script>", "", dom, flags=re.S)
print("pre-rendered:", len(dom), "bytes;", "tables in static HTML:", static.count("<table"), "; svg:", static.count("<svg"))
