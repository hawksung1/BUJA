from __future__ import annotations

import feedparser
import os
from datetime import datetime


MONEYCOMICS_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID", "UCJo6G1u0e_-wS-JQn3T-zEw")
RSS_BASE = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"


def fetch_channel_videos(channel_id: str, limit: int = 10) -> list[dict]:
    if not channel_id:
        return []
    url = RSS_BASE.format(channel_id=channel_id)
    try:
        feed = feedparser.parse(url)
        videos = []
        for entry in feed.entries[:limit]:
            published = ""
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d")
            video_id = entry.get("yt_videoid", "")
            videos.append({
                "title": entry.get("title", ""),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",
                "published": published,
                "summary": entry.get("summary", ""),
                "video_id": video_id,
            })
        return videos
    except Exception:
        return []


def fetch_moneycomics_videos(limit: int = 5) -> list[dict]:
    channel_id = MONEYCOMICS_CHANNEL_ID
    if not channel_id:
        return [
            {
                "title": "채널 ID 미설정 — .env에 YOUTUBE_CHANNEL_ID를 추가하세요",
                "url": "https://www.youtube.com/@moneymoneycomics",
                "thumbnail": "",
                "published": datetime.now().strftime("%Y-%m-%d"),
                "summary": "브라우저에서 채널 소스를 확인해 channelId를 복사하세요.",
                "video_id": "",
            }
        ]
    return fetch_channel_videos(channel_id, limit)
