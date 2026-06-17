"""
수집한 데이터를 카카오톡 메시지(200자 제한)로 포맷팅합니다.
브리핑은 3개 메시지로 나눠 발송됩니다:
1) 지수, 2) 관심 종목, 3) AI 시황 인사이트
"""

from datetime import datetime
from zoneinfo import ZoneInfo


def _arrow(change_pct: float) -> str:
    """변동률 부호에 따른 텍스트 화살표."""
    if change_pct > 0:
        return "▲"
    if change_pct < 0:
        return "▼"
    return "-"


def _fmt_price(value: float, is_index: bool) -> str:
    """지수는 소수점 2자리, 종목은 천 단위 콤마."""
    if is_index:
        return f"{value:,.2f}"
    return f"{value:,.0f}"


def _today_kst() -> str:
    """오늘 날짜 (MM/DD 형식, KST)."""
    return datetime.now(ZoneInfo("Asia/Seoul")).strftime("%m/%d")


def format_indices(indices: list) -> str:
    """지수 정보 메시지."""
    if not indices:
        return f"[{_today_kst()} 시황] 지수 데이터를 불러오지 못했습니다."

    lines = [f"[{_today_kst()} 주요 지수]"]
    for idx in indices:
        arrow = _arrow(idx["change_pct"])
        price = _fmt_price(idx["close"], is_index=True)
        lines.append(
            f"{idx['name']} {price} {arrow}{abs(idx['change_pct']):.2f}%"
        )
    return "\n".join(lines)


def format_stocks(stocks: list) -> str:
    """관심 종목 메시지."""
    if not stocks:
        return "[관심 종목] 데이터를 불러오지 못했습니다."

    lines = ["[관심 종목]"]
    for s in stocks:
        arrow = _arrow(s["change_pct"])
        price = _fmt_price(s["close"], is_index=False)
        lines.append(
            f"{s['name']} {price} {arrow}{abs(s['change_pct']):.2f}%"
        )
    return "\n".join(lines)


def format_insight(insight_text: str) -> str:
    """AI 시황 인사이트 메시지."""
    return f"[AI 시황]\n{insight_text}"


def build_all_messages(market_data: dict, insight: str) -> list:
    """3개 메시지를 리스트로 반환."""
    return [
        format_indices(market_data["indices"]),
        format_stocks(market_data["stocks"]),
        format_insight(insight),
    ]
