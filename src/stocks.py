"""
주식 데이터 수집 모듈.
FinanceDataReader로 지수와 개별 종목의 최신/전일 종가와 등락률을 가져옵니다.
"""

from datetime import datetime, timedelta
from typing import Optional

import FinanceDataReader as fdr


def _fetch_latest_two(symbol: str) -> Optional[tuple]:
    """
    심볼의 가장 최근 2영업일 데이터를 가져옵니다.
    한국 휴장일이나 미국과 시차 등으로 인해 10일 범위를 조회합니다.

    Returns:
        (최신_종가, 전일_종가) 튜플, 데이터 부족시 None
    """
    end = datetime.now()
    start = end - timedelta(days=10)

    try:
        df = fdr.DataReader(symbol, start, end)
    except Exception as e:
        print(f"[stocks] {symbol} 조회 실패: {e}")
        return None

    if df is None or len(df) < 2:
        return None

    latest = df.iloc[-1]["Close"]
    prev = df.iloc[-2]["Close"]
    return float(latest), float(prev)


def get_price_info(name: str, symbol: str) -> Optional[dict]:
    """
    종목 또는 지수의 현재 가격 정보를 dict로 반환합니다.

    Returns:
        {
            'name': str,        # 표시명
            'symbol': str,      # 심볼
            'close': float,     # 최신 종가
            'change': float,    # 변동치 (절댓값)
            'change_pct': float # 변동률 (%)
        }
    """
    result = _fetch_latest_two(symbol)
    if result is None:
        return None

    latest, prev = result
    if prev == 0:
        return None

    change = latest - prev
    change_pct = (change / prev) * 100

    return {
        "name": name,
        "symbol": symbol,
        "close": latest,
        "change": change,
        "change_pct": change_pct,
    }


def collect_all(indices: dict, watchlist: dict) -> dict:
    """
    설정된 모든 지수와 종목 데이터를 수집합니다.

    Args:
        indices: {표시명: 심볼} 형태의 지수 매핑
        watchlist: {표시명: 심볼} 형태의 종목 매핑

    Returns:
        {
            'indices': [{name, symbol, close, change, change_pct}, ...],
            'stocks':  [{name, symbol, close, change, change_pct}, ...]
        }
    """
    indices_data = []
    for name, sym in indices.items():
        info = get_price_info(name, sym)
        if info:
            indices_data.append(info)

    stocks_data = []
    for name, sym in watchlist.items():
        info = get_price_info(name, sym)
        if info:
            stocks_data.append(info)

    return {"indices": indices_data, "stocks": stocks_data}
