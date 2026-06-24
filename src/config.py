"""
관심 종목, 지수, 뉴스 소스 설정.
- 종목 코드를 추가/제거하려면 이 파일만 수정하면 됩니다.
- 한국 종목: 6자리 코드 (예: '005930' = 삼성전자)
- 미국 종목: 티커 (예: 'AAPL')
"""

# 추적할 지수: {표시명: FinanceDataReader 심볼}
INDICES_KR = {
    "코스피": "KS11",
    "코스닥": "KQ11",
}

INDICES_US = {
    "S&P500": "US500",
    "나스닥": "IXIC",
    "다우": "DJI",
}

# 관심 종목: {표시명: 심볼}
# 자유롭게 추가/제거하세요.
WATCHLIST_KR = {
    "삼성전자": "005930",
    "SK하이닉스": "000660",
    "KODEX200": "069500",    
    "KODEX KOSDAK 150": "229200",
}

WATCHLIST_US = {
    "Apple": "AAPL",
    "NVIDIA": "NVDA",
    "Tesla": "TSLA",
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

# 사용할 Gemini 모델
# - gemini-2.5-flash: 무료 티어에서 사용 가능, 매일 1회 호출 기준 무제한 수준
# - gemini-2.5-flash-lite: 더 가볍고 빠름 (필요시 변경)
GEMINI_MODEL = "gemini-2.5-flash"
