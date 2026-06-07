#!/usr/bin/env python3
"""
ADC News Generator
------------------
Reads news.json and generates:
  - index.html   (the news page)
  - rss.xml      (the RSS feed)

Run from adc/news/:
    python3 gen.py

Or from anywhere:
    python3 adc/news/gen.py
"""

import json
import html
from datetime import datetime, timezone
from pathlib import Path
from email.utils import format_datetime

# ---------------------------------------------------------------------------
# Paths - always relative to this script, so it works from any cwd
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent.resolve()
NEWS_JSON   = SCRIPT_DIR / "news.json"
INDEX_HTML  = SCRIPT_DIR / "index.html"
RSS_XML     = SCRIPT_DIR / "rss.xml"

SITE_BASE   = "https://mealman1551.github.io"
FEED_URL    = f"{SITE_BASE}/adc/news/rss.xml"
NEWS_URL    = f"{SITE_BASE}/adc/news/"

# ---------------------------------------------------------------------------
# Load items
# ---------------------------------------------------------------------------
items: list[dict] = json.loads(NEWS_JSON.read_text(encoding="utf-8"))

# Parse dates once so we can sort and format
for item in items:
    item["_dt"] = datetime.strptime(item["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)

# Most recent first
items.sort(key=lambda x: x["_dt"], reverse=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def human_date(dt: datetime) -> str:
    """June 7, 2026"""
    return dt.strftime("%B %-d, %Y")

def rfc822(dt: datetime) -> str:
    """Sat, 07 Jun 2026 00:00:00 +0000"""
    return format_datetime(dt)

def strip_html(text: str) -> str:
    """Very minimal HTML stripper for RSS descriptions."""
    import re
    return html.escape(re.sub(r"<[^>]+>", " ", text).strip())

# ---------------------------------------------------------------------------
# Build HTML articles block
# ---------------------------------------------------------------------------
def build_articles() -> str:
    parts = []
    for item in items:
        dt       = item["_dt"]
        date_iso = item["date"]
        date_str = human_date(dt)
        author   = html.escape(item["author"])
        title    = html.escape(item["title"])
        content  = item["content"]   # kept raw so inline HTML (links, <br>) works
        item_id  = html.escape(item["id"])

        parts.append(f"""\
        <article class="news-entry" id="{item_id}">
          <header>
            <h2>{title}</h2>
            <div class="news-meta">
              <time datetime="{date_iso}">{date_str}</time> ·
              <span class="news-author">by {author}</span>
            </div>
          </header>
          <p>
            {content}
          </p>
        </article>""")

    return "\n\n".join(parts)

# ---------------------------------------------------------------------------
# Full index.html
# ---------------------------------------------------------------------------
ARTICLES = build_articles()

INDEX = f"""\
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ADC News</title>
    <link
      rel="alternate"
      type="application/rss+xml"
      title="ADC News RSS"
      href="rss.xml"
    />
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

        <p>
          For the latest updates, follow the repo and check the ADC mailing list
          archives.
        </p>
      </section>
    </main>

    <footer>
      <h5>
        Made with \U0001f49a by <a href="https://github.com/Mealman1551">Mealman1551</a>
      </h5>
      <h6>\u00a9 2024 - 2026 Mealman1551 - The ADC Archiver Project</h6>
    </footer>
  </body>
</html>
"""

# ---------------------------------------------------------------------------
# RSS feed
# ---------------------------------------------------------------------------
def build_rss_items() -> str:
    parts = []
    for item in items:
        title   = html.escape(item["title"])
        desc    = strip_html(item["content"])
        pub     = rfc822(item["_dt"])
        guid    = f"{NEWS_URL}#{item['id']}"
        link    = NEWS_URL

        parts.append(f"""\
    <item>
      <title>{title}</title>
      <link>{link}</link>
      <description>{desc}</description>
      <pubDate>{pub}</pubDate>
      <guid isPermaLink="false">{guid}</guid>
    </item>""")

    return "\n\n".join(parts)

RSS = f"""\
<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>ADC News</title>
    <link>{NEWS_URL}</link>
    <description>Latest news from The ADC Archiver Project</description>
    <language>en</language>
    <lastBuildDate>{rfc822(items[0]["_dt"])}</lastBuildDate>
    <atom:link href="{FEED_URL}" rel="self" type="application/rss+xml" />

{build_rss_items()}

  </channel>
</rss>
"""

# ---------------------------------------------------------------------------
# Write output
# ---------------------------------------------------------------------------
INDEX_HTML.write_text(INDEX, encoding="utf-8")
RSS_XML.write_text(RSS, encoding="utf-8")

print(f"Generated: {INDEX_HTML}")
print(f"Generated: {RSS_XML}")
print(f"Items:     {len(items)}")
