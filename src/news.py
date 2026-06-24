"""
RSS 피드에서 최신 경제 뉴스 헤드라인을 수집합니다.
일부 피드가 실패해도 나머지에서 수집되도록 견고하게 작성됐습니다.
"""

from typing import Optional

import feedparser

from . import config


# RSS 요청 타임아웃 (초)
FEED_TIMEOUT = 8


def fetch_one(source_name: str, url: str, max_items: int) -> list:
    """
    하나의 RSS 피드에서 최신 헤드라인을 가져옵니다.

    Returns:
        [{'source': str, 'title': str}, ...] 형태의 리스트.
        실패 시 빈 리스트 반환.
    """
    try:
        # feedparser는 socket-level 타임아웃을 직접 받지 않으므로
        # request_headers로 user-agent만 지정하고, feedparser 내부 처리에 맡김
        parsed = feedparser.parse(
            url,
            request_headers={"User-Agent": "Mozilla/5.0 (stock-bot)"},
        )
    except Exception as e:
        print(f"[news] {source_name} 실패: {e}")
        return []

    if parsed.bozo and not parsed.entries:
        print(f"[news] {source_name} 파싱 실패 (bozo)")
        return []

    items = []
    for entry in parsed.entries[:max_items]:
        title = getattr(entry, "title", "").strip()
        if title:
            items.append({"source": source_name, "title": title})

    return items


def collect_all_news() -> list:
    """
    설정된 모든 RSS 피드에서 헤드라인을 수집합니다.

    Returns:
        모든 피드를 합친 헤드라인 리스트.
    """
    all_items = []
    for source_name, url in config.NEWS_FEEDS:
        items = fetch_one(source_name, url, config.NEWS_PER_FEED)
        if items:
            print(f"[news] {source_name}: {len(items)}건 수집")
            all_items.extend(items)
        else:
            print(f"[news] {source_name}: 수집 실패")

    return all_items


def format_news_for_prompt(news_items: list) -> str:
    """수집한 뉴스를 LLM 프롬프트용 텍스트로 정리."""
    if not news_items:
        return "(뉴스 헤드라인 없음)"

    lines = []
    for item in news_items:
        lines.append(f"[{item['source']}] {item['title']}")
    return "\n".join(lines)
