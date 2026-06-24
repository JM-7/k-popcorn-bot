"""
관심 종목, 지수, 환율, 뉴스 소스 설정.
- 추가/제거하려면 이 파일만 수정하면 됩니다.
- 한국 종목: 6자리 코드 (예: '005930' = 삼성전자)
- 미국 종목: 티커 (예: 'AAPL')
- 환율: ISO 통화 코드 (예: 'USD', 'GBP', 'EUR')
"""

INDICES_KR = {
    "코스피": "KS11",
    "코스닥": "KQ11",
}

INDICES_US = {
    "S&P500": "US500",
    "나스닥": "IXIC",
}

EXCHANGE_RATES = {
    "달러/원": "USD",
    "파운드/원": "GBP",
    "유로/원": "EUR",
}

# 관심 종목: {표시명: 심볼}
WATCHLIST_KR = {
    "삼성전자": "005930",
    "SK하이닉스": "000660",
    "코덱스 200": "069500",
    "코스닥 150": "229200",
}

WATCHLIST_US = {
    "Micron": "MU",
    "NVIDIA": "NVDA",
    "Evemetal": "EMAT",
}

NEWS_FEEDS = [
    ("한경", "https://www.hankyung.com/feed/economy"),
    ("매경", "https://www.mk.co.kr/rss/30100041/"),
    ("연합뉴스", "https://www.yna.co.kr/rss/economy.xml"),
    ("Yahoo Finance", "https://finance.yahoo.com/news/rssindex"),
]

NEWS_PER_FEED = 5
DEFAULT_LINK_URL = "https://finance.naver.com"

# 사용할 Gemini 모델 — 무료 티어 한도 (2025-12 축소 이후)
# - gemini-2.5-flash-lite: RPD 1,000, RPM 15 (권장: 매시 발송 안정)
# - gemini-2.5-flash:      RPD   250, RPM 10 (16회/일 발송엔 빠듯)
# - gemini-2.0-flash:      RPD 1,000, RPM 15 (구세대, 안정적)
GEMINI_MODEL = "gemini-2.5-flash-lite"
