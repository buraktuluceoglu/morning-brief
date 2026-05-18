import re
from datetime import datetime, timezone
from urllib.parse import urlparse, urlunparse

import feedparser

FEEDS = [
    ("https://raw.githubusercontent.com/taobojlen/anthropic-rss-feed/main/anthropic_news_rss.xml", "Anthropic News"),
    ("https://raw.githubusercontent.com/cnzhujie/ai-rss-feed/main/rss/deeplearning_the_batch_rss.xml", "The Batch"),
    ("https://simonwillison.net/atom/everything", "Simon Willison"),
    ("https://raw.githubusercontent.com/cnzhujie/ai-rss-feed/main/rss/huggingface_blog_rss.xml", "HuggingFace Blog"),
    ("https://feeds.feedburner.com/TheHackersNews", "The Hacker News"),
    ("https://krebsonsecurity.com/feed", "Krebs on Security"),
    ("https://www.bleepingcomputer.com/feed/", "BleepingComputer"),
    ("https://www.darkreading.com/rss.xml", "Dark Reading"),
    ("https://export.arxiv.org/rss/cs.AI", "arXiv cs.AI"),
    ("https://export.arxiv.org/rss/cs.CR", "arXiv cs.CR"),
]


def collect() -> dict:
    items = []
    seen_urls: set[str] = set()
    for feed_url, source in FEEDS:
        try:
            feed = feedparser.parse(feed_url, agent="morning-brief/1.0")
        except Exception as e:
            print(f"Feed error [{source}]: {e}")
            continue
        for entry in feed.entries[:20]:
            url = _normalize_url(entry.get("link", ""))
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            items.append({
                "title": entry.get("title", "").strip(),
                "url": url,
                "source": source,
                "published_at": _parse_date(entry),
                "snippet": _snippet(entry),
            })
    return {"items": items}


def _normalize_url(url: str) -> str:
    if not url:
        return ""
    p = urlparse(url)
    return urlunparse((p.scheme, p.netloc, p.path.rstrip("/"), "", "", "")).lower()


def _parse_date(entry) -> str:
    if getattr(entry, "published_parsed", None):
        try:
            return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()
        except Exception:
            pass
    return datetime.now(timezone.utc).isoformat()


def _snippet(entry) -> str:
    raw = getattr(entry, "summary", "") or ""
    return re.sub(r"<[^>]+>", "", raw)[:300].strip()
