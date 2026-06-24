"""
주식 데이터 수집 모듈.
FinanceDataReader로 지수와 개별 종목의 최신/전일 종가와 등락률을 가져옵니다.

NaN 방어:
- FDR이 가끔 NaN이 섞인 데이터를 반환하므로 dropna 처리
- 환율 데이터는 NaN이 잦은데, 이 모듈은 주로 지수·종목용
  (환율은 별도의 exchange.py 모듈을 사용)
"""

import math
from datetime import datetime, timedelta
from typing import Optional

import FinanceDataReader as fdr


def _fetch_latest_two(symbol: str) -> Optional[tuple]:
    """
    심볼의 가장 최근 2영업일 데이터를 가져옵니다.
    NaN을 자동 제거하므로 안정적입니다.

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

    if df is None or df.empty:
        print(f"[stocks] {symbol}: 빈 데이터")
        return None

    # NaN 행 제거 (가끔 Close에 NaN 섞임)
    if "Close" not in df.columns:
        print(f"[stocks] {symbol}: Close 컬럼 없음")
        return None
    df = df.dropna(subset=["Close"])

    if len(df) < 2:
        print(f"[stocks] {symbol}: 영업일 데이터 부족")
        return None

    latest = float(df.iloc[-1]["Close"])
    prev = float(df.iloc[-2]["Close"])

    # NaN/0 최종 방어
    if math.isnan(latest) or math.isnan(prev) or prev == 0:
        print(f"[stocks] {symbol}: 잘못된 값 (latest={latest}, prev={prev})")
        return None

    return latest, prev


def get_price_info(name: str, symbol: str) -> Optional[dict]:
    """
    종목 또는 지수의 현재 가격 정보를 dict로 반환합니다.
    """
    result = _fetch_latest_two(symbol)
    if result is None:
        return None

    latest, prev = result
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
