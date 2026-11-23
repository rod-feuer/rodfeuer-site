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
MODIFIED = "2026-11-23"
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
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
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
person = {"@type": "Person", "@id": "https://rodfeuer.com/#rod", "name": "Rod Feuer", "url": SITE + "/", "image": SITE + "/headshot.jpg", "description": "Rod Feuer co-founded Costello, acquired by Salesloft, and advises tech companies on strategy and positioning. He writes about AI.", "sameAs": [LINKEDIN, X_PROFILE]}
GOATCOUNTER = '<script data-goatcounter="https://rodfeuer.goatcounter.com/count"\n        async src="//gc.zgo.at/count.js"></script>\n'
article_ld = {
    "@context": "https://schema.org", "@type": "Article", "headline": TITLE, "description": DESC,
    "author": person, "publisher": person, "inLanguage": "en",
    "datePublished": PUBLISHED, "dateModified": MODIFIED,
    "mainEntityOfPage": SITE + "/where-the-ai-money-goes/", "image": SITE + "/og.png",
}
head_extra = ('<script type="application/ld+json">' + json.dumps(article_ld) + '</script>\n'
  '<style>.byline{font:600 15px/1.3 var(--sans);color:var(--text-secondary);margin:0 0 6px}.byline a{color:inherit}</style>\n'
  + GOATCOUNTER)
cut = src.index("</style>") + len("</style>")
body = src[cut:]
# byline + machine-readable date (key findings now come from build_article.py)
byline = ('<p class="byline">By <a href="' + SITE + '/" rel="author">Rod Feuer</a> \u00b7 '
          '<time datetime="' + PUBLISHED + '">November 2026</time></p>\n')

i = body.index('<section class="keyfacts"')
body = body[:i] + byline + body[i:]
# count clicks on outbound links (GoatCounter reads data-goatcounter-click); one event name per link: ext-<host>/<first path segment>
def tag_outbound(m):
    host, path = m.group(2), m.group(3).strip("/").split("/")[0]
    return m.group(1) + ' data-goatcounter-click="ext-' + host + ("/" + path if path else "") + '"'
body = re.sub(r'(<a href="https?://(?!rodfeuer\.com)([^/"]+)(/[^"]*)?")', tag_outbound, body)
# the one SVG icon without a label is decorative; the routes diagram needs a label
body = body.replace('<svg width="18" height="18" viewBox="0 0 18 18" style="vertical-align:-4px;margin-right:4px">',
                    '<svg width="18" height="18" viewBox="0 0 18 18" style="vertical-align:-4px;margin-right:4px" aria-hidden="true">', 1)
body = body.replace('<svg class="routes" width="100%" viewBox="0 0 793 534" role="img">',
                    '<svg class="routes" width="100%" viewBox="0 0 793 534" role="img" aria-label="Two routes into records and rules: become a new system of record, or become the system of intelligence">', 1)
PRIVACY = '<p style="font:400 14px/1.4 var(--sans);color:var(--text-muted);max-width:720px;margin:48px auto 0;padding:0 20px">This site counts page views and link clicks with GoatCounter, which sets no cookies and does not track you across sites.</p>'
out = head_meta + src[:cut] + head_extra + "\n</head>\n<body>\n" + body + PRIVACY + "\n</body>\n</html>\n"
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
