#!/usr/bin/env python3

import html
from datetime import datetime, timezone
from pathlib import Path
from email.utils import format_datetime

SCRIPT_DIR = Path(__file__).parent.resolve()
POSTS_DIR = SCRIPT_DIR / "posts"
INDEX_HTML = SCRIPT_DIR / "index.html"
RSS_XML = SCRIPT_DIR / "rss.xml"

SITE_BASE = "https://mealman1551.github.io"
FEED_URL = f"{SITE_BASE}/adc/news/rss.xml"
NEWS_URL = f"{SITE_BASE}/adc/news/"

def parse_post(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()

    meta = {}
    i = 0

    while i < len(lines) and lines[i].strip():
        if ":" in lines[i]:
            k, v = lines[i].split(":", 1)
            meta[k.strip().lower()] = v.strip()
        i += 1

    content = "\n".join(lines[i:]).strip()

    dt = datetime.strptime(meta["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)

    return {
        "id": path.stem,
        "title": meta.get("title", ""),
        "date": meta.get("date", ""),
        "author": meta.get("author", ""),
        "content": content,
        "_dt": dt
    }

def load_posts():
    if not POSTS_DIR.exists():
        return []

    posts = [parse_post(p) for p in POSTS_DIR.glob("*.md")]
    posts.sort(key=lambda x: x["_dt"], reverse=True)
    return posts

def human_date(dt: datetime):
    return f"{dt.strftime('%B')} {dt.day}, {dt.year}"

def rfc822(dt: datetime):
    return format_datetime(dt)

def strip_html(text: str):
    import re
    return html.escape(re.sub(r"<[^>]+>", " ", text).strip())

posts = load_posts()

def build_articles():
    parts = []

    for p in posts:
        parts.append(f"""
        <article class="news-entry" id="{html.escape(p['id'])}">
          <header>
            <h2>{html.escape(p['title'])}</h2>
            <div class="news-meta">
              <time datetime="{p['date']}">{human_date(p['_dt'])}</time> ·
              <span class="news-author">by {html.escape(p['author'])}</span>
            </div>
          </header>
          <p>
            {p['content']}
          </p>
        </article>
        """)

    return "\n".join(parts)

def build_rss_items():
    parts = []

    for p in posts:
        parts.append(f"""
    <item>
      <title>{html.escape(p['title'])}</title>
      <link>{NEWS_URL}</link>
      <description>{strip_html(p['content'])}</description>
      <pubDate>{rfc822(p['_dt'])}</pubDate>
      <guid isPermaLink="false">{NEWS_URL}#{p['id']}</guid>
    </item>
        """)

    return "\n".join(parts)

ARTICLES = build_articles()

INDEX = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ADC News</title>
  <link rel="alternate" type="application/rss+xml" title="ADC News RSS" href="rss.xml" />
  <link rel="stylesheet" href="../stylesheets/adcnew-v2.css" />
  <link rel="stylesheet" href="../stylesheets/adc-navbar.css" />
  <link rel="stylesheet" href="../stylesheets/adc-panel.css" />
</head>
<body>
    <nav class="adc-navbar" aria-label="ADC main navigation">
      <div class="nav-brand">
        <a href="../index.html" class="nav-logo">
          <img
            src="/img/ADC(ArchivedDataCodec).png"
            alt="ADC Logo"
            width="200"
            class="nav-logo-image"
          />
          <span>ArchivedDataCodec</span>
        </a>
      </div>
      <ul class="nav-links">
        <li><a href="../index.html">Home</a></li>
        <li><a href="index.html">News</a></li>
        <li><a href="../downloads/index.html">Downloads</a></li>
        <li><a href="../community/index.html">Community</a></li>
        <li><a href="../features/index.html">Features</a></li>
        <li>
          <a
            href="https://github.com/Mealman1551/ArchivedDataCodec"
            target="_blank"
            rel="noopener noreferrer"
          >
            <img src="/img/socials/github.png" alt="GitHub Logo" width="24" />
            <span>GitHub</span>
          </a>
        </li>
      </ul>
    </nav>

<main>
<section class="adc-panel">
<h1>News</h1>

{ARTICLES}

<p>For the latest updates, follow the repo and RSS feed.</p>
</section>
</main>
<hr />
<p>For the latest updates, follow the RSS feed.</p>
<a href="https://mealman1551.github.io/adc/news/rss.xml">
  <img src="/img/svg/icon.svg" alt="RSS Icon" width="24" />
</a>

<footer>
<h5>Made with 💚 by <a href="https://github.com/Mealman1551">Mealman1551</a></h5>
<h6>© 2024 - 2026 Mealman1551</h6>
</footer>

</body>
</html>
"""

RSS = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
<title>ADC News</title>
<link>{NEWS_URL}</link>
<description>Latest news from ADC</description>
<language>en</language>
<lastBuildDate>{rfc822(posts[0]['_dt']) if posts else ''}</lastBuildDate>
<atom:link href="{FEED_URL}" rel="self" type="application/rss+xml" />

{build_rss_items()}

</channel>
</rss>
"""

INDEX_HTML.write_text(INDEX, encoding="utf-8")
RSS_XML.write_text(RSS, encoding="utf-8")

print("Generated index.html and rss.xml")
print(f"Posts: {len(posts)}")