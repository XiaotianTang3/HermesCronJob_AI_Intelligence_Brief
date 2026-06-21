#!/usr/bin/env python3
"""Fast, bounded AI investment/funding RSS probe for Hermes cron.

Collects candidate financing/funding leads only. The agent must still verify
announcement date, source authority, amount/stage/investors, and AI relevance.
"""
from __future__ import annotations

import email.utils
import html
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

UA = "Mozilla/5.0 (compatible; Hermes-AI-Investment-RSS-Probe/1.0)"
TIMEOUT = 8
DEADLINE_SEC = 95
LIMIT_PER_SOURCE = 12
MAX_DESC = 420

INVISIBLE_UNICODE = {
    ord("\u200b"): None,
    ord("\u200c"): None,
    ord("\u200d"): None,
    ord("\ufeff"): None,
}

# Curated discovery sources. These are leads, not final authority.
SOURCES = [
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "type": "rss"},
    {"name": "TechCrunch Startups", "url": "https://techcrunch.com/category/startups/feed/", "type": "rss"},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/category/ai/feed", "type": "rss"},
    {"name": "PR Newswire AI search", "url": "https://www.prnewswire.com/rss/news-releases-list.rss", "type": "rss"},
]

SEARCHES = [
    "AI startup funding raises seed Series A Series B when:3d",
    "artificial intelligence startup funding venture capital when:3d",
    "AI agent startup raises funding a16z Sequoia Lightspeed when:7d",
    "AI infrastructure model lab funding round when:7d",
    "机器人 大模型 智能体 AI 融资 完成 亿元 when:7d",
    "人工智能 公司 完成 融资 领投 when:7d",
    "具身智能 世界模型 融资 when:7d",
]


def clean_text(s: str) -> str:
    s = html.unescape(s or "")
    s = s.translate(INVISIBLE_UNICODE)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s).strip()


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
    items: list[dict] = []
    for item in root.findall(".//item")[:limit]:
        title = clean_text(item.findtext("title") or "")
        link = clean_text(item.findtext("link") or "")
        pub = parse_date(item.findtext("pubDate") or item.findtext("published") or "")
        desc = clean_text(item.findtext("description") or item.findtext("summary") or "")[:MAX_DESC]
        if title or link:
            items.append({"title": title, "url": link, "published": pub, "summary": desc})
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


def google_news_url(query: str, *, zh: bool = False) -> str:
    q = urllib.parse.quote(query)
    if zh:
        return f"https://news.google.com/rss/search?q={q}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"
    return f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"


def main() -> int:
    started = time.time()
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "note": "AI funding candidate leads only. Verify date/source/amount/stage/investors before inclusion; drop stale resurfaced items.",
        "sources": [],
        "stats": {"ok": 0, "errors": 0, "items": 0, "elapsed_sec": 0},
    }
    source_defs = list(SOURCES)
    for q in SEARCHES:
        source_defs.append({
            "name": f"Google News: {q[:56]}",
            "url": google_news_url(q, zh=bool(re.search(r"[\u4e00-\u9fff]", q))),
            "type": "google_news",
            "query": q,
        })

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
            items = parse_feed(fetch(src["url"]))
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
