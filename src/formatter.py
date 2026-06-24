"""
수집한 데이터를 카카오톡 메시지(200자 제한)로 포맷팅합니다.

메시지 구성:
1) 지수·환율
2) 관심 종목
3+) AI 시황 인사이트 (시간대 라벨이 이미 포함된 텍스트를 200자씩 분할)
"""

from datetime import datetime
from zoneinfo import ZoneInfo


KAKAO_MAX_LEN = 200


def _arrow(change_pct: float) -> str:
    if change_pct > 0:
        return "▲"
    if change_pct < 0:
        return "▼"
    return "-"


def _fmt_price(value: float, is_index: bool) -> str:
    if is_index:
        return f"{value:,.2f}"
    return f"{value:,.0f}"


def _now_kst_str() -> str:
    """현재 KST '월/일 시:분' 형식."""
    return datetime.now(ZoneInfo("Asia/Seoul")).strftime("%m/%d %H:%M")


def format_indices(indices: list) -> str:
    """지수+환율 정보 메시지."""
    if not indices:
        return f"[{_now_kst_str()}] 지수 데이터를 불러오지 못했습니다."

    lines = [f"[{_now_kst_str()} 주요 지수]"]
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
    """문장 경계에서 우선 자르고, 못 자르면 글자 단위."""
    if len(text) <= max_len:
        return text

    candidate = text[:max_len]
    for sep in ["다.\n", "다.", ".\n", ".", "\n"]:
        idx = candidate.rfind(sep)
        if idx > max_len * 0.5:
            return candidate[: idx + len(sep)]

    return candidate


def format_insight(insight_text: str) -> list:
    """
    AI 시황을 200자 이하 메시지들로 분할.
    insight_text에는 이미 시간대 라벨 헤더가 포함돼 있으므로
    그대로 200자 단위로 자릅니다.
    """
    text = (insight_text or "").strip()
    if not text:
        return ["[AI 시황] (생성 실패)"]

    messages = []
    remaining = text
    while remaining:
        chunk = _split_chunk(remaining, KAKAO_MAX_LEN)
        messages.append(chunk)
        remaining = remaining[len(chunk):].lstrip()

    return messages


def build_all_messages(market_data: dict, insight: str) -> list:
    """전체 메시지 리스트 반환 (3~5개)."""
    messages = [
        format_indices(market_data["indices"]),
        format_stocks(market_data["stocks"]),
    ]
    messages.extend(format_insight(insight))
    return messages
