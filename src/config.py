"""
관심 종목, 지수, 환율, 뉴스 소스 설정.
- 추가/제거하려면 이 파일만 수정하면 됩니다.
- 한국 종목: 6자리 코드 (예: '005930' = 삼성전자)
- 미국 종목: 티커 (예: 'AAPL')
- 환율: FDR 심볼 (예: 'USD/KRW')
"""

# 추적할 지수: {표시명: FinanceDataReader 심볼}
INDICES_KR = {
    "코스피": "KS11",
    "코스닥": "KQ11",
}

INDICES_US = {
    "S&P500": "US500",
    "나스닥": "IXIC",
}

# 환율: {표시명: FDR 심볼}
# 표시명은 짧을수록 메시지 가독성 좋음
EXCHANGE_RATES = {
    "달러/원": "USD",
    "파운드/원": "GBP",
    "유로/원": "EUR",
}

# 관심 종목: {표시명: 심볼}
# 자유롭게 추가/제거하세요.
WATCHLIST_KR = {
    "삼성전자": "005930",
    "SK하이닉스": "000660",
    "KODEX 200": "069500",
    "KOSDAK 150": "229200",
}

WATCHLIST_US = {
    "MICRON": "MU",
    "NVIDIA": "NVDA",
    "EVOLU": "EMAT",
}

# RSS 뉴스 소스 (한 곳이 실패해도 다른 곳에서 가져옴)
NEWS_FEEDS = [
    # 한국 경제 뉴스
    ("한경", "https://www.hankyung.com/feed/economy"),
    ("매경", "https://www.mk.co.kr/rss/30100041/"),
    ("연합뉴스", "https://www.yna.co.kr/rss/economy.xml"),
    # 미국 경제 뉴스
    ("Yahoo Finance", "https://finance.yahoo.com/news/rssindex"),
]

# 뉴스 소스당 가져올 최대 헤드라인 수
NEWS_PER_FEED = 5

# 메시지 발송 시 사용할 링크 (카카오 메시지 버튼 URL)
DEFAULT_LINK_URL = "https://finance.naver.com"

# 사용할 Gemini 모델 — 무료 티어 한도 (2025-12 축소 이후)
# - gemini-2.5-flash-lite: RPD 1,000, RPM 15 (권장: 매시 발송 안정)
# - gemini-2.5-flash:      RPD   250, RPM 10 (16회/일 발송엔 빠듯)
# - gemini-2.0-flash:      RPD 1,000, RPM 15 (구세대, 안정적)
GEMINI_MODEL = "gemini-2.5-flash-lite"
