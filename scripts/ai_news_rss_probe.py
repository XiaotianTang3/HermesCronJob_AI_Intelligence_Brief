#!/usr/bin/env python3
"""Fast, bounded AI news RSS probe for Hermes cron.

Fetches a curated set of high-signal RSS feeds and Google News RSS searches with
strict timeouts. Emits compact JSON for the AI briefing agent. This is source
collection only; the agent must still apply relevance filtering and source checks.
"""
from __future__ import annotations

import email.utils
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

UA = "Mozilla/5.0 (compatible; Hermes-AI-News-RSS-Probe/1.0)"
# Cron kills pre-run scripts at 120s. There are 10 sources below, so a per-source
# timeout of 18s can exceed the cron budget even when everything is working as
# designed. Keep individual fetches and the whole probe bounded.
TIMEOUT = 8
DEADLINE_SEC = 95
LIMIT_PER_SOURCE = 12
MAX_DESC = 360

SOURCES = [
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "type": "rss"},
    {"name": "The Verge AI", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "type": "rss"},
    {"name": "TechCrunch Full", "url": "https://techcrunch.com/feed/", "type": "rss"},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed", "type": "rss"},
    {"name": "OpenAI News", "url": "https://openai.com/news/rss.xml", "type": "rss"},
    {"name": "Google AI Blog", "url": "https://blog.google/technology/ai/rss/", "type": "rss"},
]

SEARCHES = [
    "OpenAI Anthropic Google DeepMind Microsoft Meta Nvidia AI product funding regulation when:2d",
    "AI startup funding acquisition IPO May 2026 when:3d",
    "China AI startup model regulation chip export controls when:3d",
    "Thinking Machines Lab Mira Murati when:7d",
]


INVISIBLE_UNICODE = {
    ord("\u200b"): None,  # zero-width space
    ord("\u200c"): None,  # zero-width non-joiner
    ord("\u200d"): None,  # zero-width joiner
    ord("\ufeff"): None,  # byte-order mark / zero-width no-break space
}


def clean_text(s: str) -> str:
    s = html.unescape(s or "")
    s = s.translate(INVISIBLE_UNICODE)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse_date(s: str) -> str:
    if not s:
        return ""
    try:
        dt = email.utils.parsedate_to_datetime(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    except Exception:
        return s.strip()


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read(2_000_000)


def parse_feed(data: bytes, limit: int = LIMIT_PER_SOURCE) -> list[dict]:
    root = ET.fromstring(data)
    items = []
    for item in root.findall(".//item")[:limit]:
        title = clean_text(item.findtext("title") or "")
        link = clean_text(item.findtext("link") or "")
        pub = parse_date(item.findtext("pubDate") or item.findtext("published") or "")
        desc = clean_text(item.findtext("description") or item.findtext("summary") or "")[:MAX_DESC]
        if title or link:
            items.append({"title": title, "url": link, "published": pub, "summary": desc})
    # Atom fallback
    ns = {"a": "http://www.w3.org/2005/Atom"}
    if not items:
        for entry in root.findall(".//a:entry", ns)[:limit]:
            title = clean_text(entry.findtext("a:title", default="", namespaces=ns))
            link_el = entry.find("a:link", ns)
            link = link_el.attrib.get("href", "") if link_el is not None else ""
            pub = parse_date(entry.findtext("a:updated", default="", namespaces=ns) or entry.findtext("a:published", default="", namespaces=ns))
            desc = clean_text(entry.findtext("a:summary", default="", namespaces=ns) or entry.findtext("a:content", default="", namespaces=ns))[:MAX_DESC]
            if title or link:
                items.append({"title": title, "url": link, "published": pub, "summary": desc})
    return items


def google_news_url(query: str) -> str:
    q = urllib.parse.quote(query)
    return f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"


def main() -> int:
    started = time.time()
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "note": "Pre-fetched bounded RSS/search candidates. Treat as leads; include only verified, relevant items.",
        "sources": [],
        "stats": {"ok": 0, "errors": 0, "items": 0, "elapsed_sec": 0},
    }

    source_defs = list(SOURCES) + [
        {"name": f"Google News: {q[:48]}", "url": google_news_url(q), "type": "google_news", "query": q}
        for q in SEARCHES
    ]

    for src in source_defs:
        if time.time() - started > DEADLINE_SEC:
            result["sources"].append({
                "name": "deadline",
                "type": "guard",
                "items": [],
                "error": f"Global deadline {DEADLINE_SEC}s reached; remaining sources skipped",
            })
            result["stats"]["errors"] += 1
            break
        entry = {k: v for k, v in src.items() if k != "url"}
        entry["url"] = src["url"]
        try:
            data = fetch(src["url"])
            items = parse_feed(data)
            entry["items"] = items
            entry["error"] = None
            result["stats"]["ok"] += 1
            result["stats"]["items"] += len(items)
        except Exception as e:
            entry["items"] = []
            entry["error"] = f"{type(e).__name__}: {e}"
            result["stats"]["errors"] += 1
        result["sources"].append(entry)

    result["stats"]["elapsed_sec"] = round(time.time() - started, 2)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
