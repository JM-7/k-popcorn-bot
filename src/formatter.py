"""
수집한 데이터를 카카오톡 메시지(200자 제한)로 포맷팅합니다.

메시지 구성:
1) 지수
2) 관심 종목
3+) AI 시황 인사이트 (길이에 따라 1~3개 메시지로 자동 분할)
"""

from datetime import datetime
from zoneinfo import ZoneInfo


# 카카오 텍스트 템플릿 한 메시지의 최대 길이
KAKAO_MAX_LEN = 200


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


def _split_chunk(text: str, max_len: int) -> str:
    """
    문장 경계(마침표/줄바꿈)에서 우선 자르고, 못 자르면 글자 단위로 자릅니다.
    너무 짧게 자르는 것도 방지합니다.
    """
    if len(text) <= max_len:
        return text

    candidate = text[:max_len]
    # 우선순위: '다.\n' > '다.' > '.\n' > '.' > '\n'
    for sep in ["다.\n", "다.", ".\n", ".", "\n"]:
        idx = candidate.rfind(sep)
        if idx > max_len * 0.5:  # 절반 이하로는 안 자름
            return candidate[: idx + len(sep)]

    # 마땅한 경계가 없으면 글자 단위로
    return candidate


def format_insight(insight_text: str) -> list:
    """
    AI 시황 인사이트를 200자 이하 메시지들로 분할.

    Returns:
        분할된 메시지 리스트 (1~여러 개).
        첫 메시지에만 "[AI 시황]" 헤더 포함.
    """
    header = "[AI 시황]\n"
    text = (insight_text or "").strip()

    if not text:
        return [header + "(생성 실패)"]

    messages = []

    # 첫 메시지: 헤더 포함
    first_capacity = KAKAO_MAX_LEN - len(header)
    first_chunk = _split_chunk(text, first_capacity)
    messages.append(header + first_chunk)
    remaining = text[len(first_chunk):].lstrip()

    # 나머지: 헤더 없이
    while remaining:
        chunk = _split_chunk(remaining, KAKAO_MAX_LEN)
        messages.append(chunk)
        remaining = remaining[len(chunk):].lstrip()

    return messages


def build_all_messages(market_data: dict, insight: str) -> list:
    """
    전체 메시지 리스트를 반환합니다.
    시황 길이에 따라 총 3~5개의 메시지가 나올 수 있습니다.
    """
    messages = [
        format_indices(market_data["indices"]),
        format_stocks(market_data["stocks"]),
    ]
    messages.extend(format_insight(insight))
    return messages
