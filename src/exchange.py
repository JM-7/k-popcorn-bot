"""
환율 수집 모듈.

FinanceDataReader가 환율 분야에서는 NaN/누락이 잦아서,
ECB(유럽중앙은행) 데이터 기반 무료 API인 Frankfurter를 사용합니다.

Frankfurter API 특징:
- API 키 불필요, 완전 무료
- 모든 주요 통화 안정 지원 (USD/EUR/GBP/JPY/CNY 등)
- HTTPS, 영업일 갱신
"""

from datetime import datetime, timedelta
from typing import Optional

import requests


FRANKFURTER_BASE = "https://api.frankfurter.app"
HTTP_TIMEOUT = 8


def get_rate_to_krw(currency_code: str) -> Optional[dict]:
    """
    특정 통화의 원화 환율과 전일대비 등락률을 반환합니다.

    Args:
        currency_code: ISO 통화 코드 (예: 'USD', 'EUR', 'GBP')

    Returns:
        {
            'close': float,      # 최신 환율 (1 통화당 원화)
            'change': float,     # 전일대비 변동치
            'change_pct': float, # 전일대비 변동률 (%)
        }
        실패 시 None
    """
    # 최근 10일 범위 조회 → 영업일 데이터만 응답에 포함됨
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=10)

    url = (
        f"{FRANKFURTER_BASE}/{start_date}.."
        f"?from={currency_code}&to=KRW"
    )

    try:
        response = requests.get(url, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"[exchange] {currency_code}/KRW 조회 실패: {e}")
        return None

    rates = data.get("rates", {})
    if not rates:
        print(f"[exchange] {currency_code}/KRW: 빈 응답")
        return None

    # 날짜 오름차순 정렬 후 최근 2영업일 선택
    sorted_dates = sorted(rates.keys())
    if len(sorted_dates) < 2:
        print(f"[exchange] {currency_code}/KRW: 영업일 데이터 부족")
        return None

    latest = rates[sorted_dates[-1]].get("KRW")
    prev = rates[sorted_dates[-2]].get("KRW")

    if latest is None or prev is None or prev == 0:
        print(f"[exchange] {currency_code}/KRW: 가격 데이터 없음")
        return None

    change = latest - prev
    change_pct = (change / prev) * 100

    return {
        "close": float(latest),
        "change": float(change),
        "change_pct": float(change_pct),
    }


def collect_exchange_rates(rates_config: dict) -> list:
    """
    설정된 모든 환율을 수집합니다.

    Args:
        rates_config: {표시명: 통화코드} 형태의 dict (예: {"달러/원": "USD"})

    Returns:
        [{name, symbol, close, change, change_pct}, ...] 형태의 리스트.
        실패한 환율은 건너뜁니다.
    """
    results = []
    for display_name, currency in rates_config.items():
        info = get_rate_to_krw(currency)
        if info is None:
            continue
        results.append({
            "name": display_name,
            "symbol": f"{currency}/KRW",
            **info,
        })
    return results
