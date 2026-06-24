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


def format_insight(insight_text: str) -> list:
    """
    AI 시황 인사이트를 500자 이하 메시지들로 분할.
    문장 단위로 자르려 시도하고, 안 되면 글자 단위로 자릅니다.
    """
    header = "[AI 시황]\n"
    max_per_msg = 500
    first_msg_capacity = max_per_msg - len(header)

    text = insight_text.strip()
    if not text:
        return [header + "(생성 실패)"]

    messages = []
    
    # 첫 메시지: 헤더 포함
    first_chunk = _split_chunk(text, first_msg_capacity)
    messages.append(header + first_chunk)
    text = text[len(first_chunk):].lstrip()

    # 나머지: 헤더 없이 이어붙이기
    while text:
        chunk = _split_chunk(text, max_per_msg)
        messages.append(chunk)
        text = text[len(chunk):].lstrip()

    return messages


def _split_chunk(text: str, max_len: int) -> str:
    """문장 경계(마침표/줄바꿈)에서 우선 자르고, 못 자르면 글자 단위로 자름."""
    if len(text) <= max_len:
        return text

    # 마침표 또는 줄바꿈에서 자르기 시도
    candidate = text[:max_len]
    for sep in ["다.", ".\n", ".", "\n"]:
        idx = candidate.rfind(sep)
        if idx > max_len * 0.5:  # 너무 짧게 자르지는 않음
            return candidate[: idx + len(sep)]

    # 못 자르면 그냥 글자 단위
    return candidate


def build_all_messages(market_data: dict, insight: str) -> list:
    """메시지 리스트로 반환 (시황 길이에 따라 4~5개)."""
    messages = [
        format_indices(market_data["indices"]),
        format_stocks(market_data["stocks"]),
    ]
    messages.extend(format_insight(insight))  # 시황은 여러 메시지로 분할 가능
    return messages
