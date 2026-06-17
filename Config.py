"""
관심 종목과 지수 설정.
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
    "NAVER": "035420",
}

WATCHLIST_US = {
    "Apple": "AAPL",
    "NVIDIA": "NVDA",
    "Tesla": "TSLA",
}

# 메시지 발송 시 사용할 링크 (카카오 메시지 버튼 URL)
# 카카오 개발자 콘솔 > 앱 > 플랫폼에 등록된 도메인이어야 합니다.
DEFAULT_LINK_URL = "https://finance.naver.com"

# 사용할 Claude 모델 (인사이트 생성용)
CLAUDE_MODEL = "claude-sonnet-4-6"
