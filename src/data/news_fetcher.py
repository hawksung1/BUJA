from __future__ import annotations

import feedparser
import requests
from datetime import datetime


GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"


def fetch_google_news(query: str = "주식 투자", limit: int = 15) -> list[dict]:
    url = GOOGLE_NEWS_RSS.format(query=requests.utils.quote(query))
    try:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:limit]:
            published = ""
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d %H:%M")
            source = ""
            if isinstance(entry.get("source"), dict):
                source = entry["source"].get("title", "")
            items.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "source": source or "Google뉴스",
                "published": published,
                "summary": entry.get("summary", ""),
            })
        return items
    except Exception:
        return []


def fetch_naver_finance_news(limit: int = 10) -> list[dict]:
    try:
        from bs4 import BeautifulSoup
        url = "https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        items = []
        for a in soup.select("dd.articleSubject a")[:limit]:
            items.append({
                "title": a.get_text(strip=True),
                "link": "https://finance.naver.com" + a["href"],
                "source": "네이버금융",
                "published": datetime.now().strftime("%Y-%m-%d"),
                "summary": "",
            })
        return items
    except Exception:
        return []


def fetch_all_news(query: str = "주식 증시") -> list[dict]:
    google = fetch_google_news(query=query, limit=15)
    naver = fetch_naver_finance_news(limit=10)
    combined = google + naver
    seen: set[str] = set()
    unique = []
    for item in combined:
        if item["title"] not in seen:
            seen.add(item["title"])
            unique.append(item)
    return unique
