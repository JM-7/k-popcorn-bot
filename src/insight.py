"""
OpenAI API를 사용해 시장 인사이트와 전일 뉴스 요약을 생성합니다.
Responses API의 web_search 도구로 최신 정보를 검색해 반영합니다.
"""

import os

from openai import OpenAI

from . import config


SYSTEM_INSTRUCTIONS = """당신은 한국과 미국 주식 시장을 매일 아침 브리핑하는 애널리스트입니다.
간결하고 객관적이며 사실 기반으로 작성하세요.
과장된 표현, 투자 권유, "반드시" "확실하다" 같은 단정적 표현은 피하세요."""


def _format_market_data(market_data: dict) -> str:
    """수집된 시장 데이터를 프롬프트용 텍스트로 정리."""
    lines = ["[지수]"]
    for idx in market_data["indices"]:
        lines.append(
            f"- {idx['name']}: {idx['close']:.2f} ({idx['change_pct']:+.2f}%)"
        )

    lines.append("\n[관심 종목]")
    for stock in market_data["stocks"]:
        lines.append(
            f"- {stock['name']}: {stock['close']:,.0f} ({stock['change_pct']:+.2f}%)"
        )

    return "\n".join(lines)


def generate_insight(market_data: dict) -> str:
    """
    시장 데이터와 웹 검색을 바탕으로 한국어 시황 인사이트를 생성합니다.

    Returns:
        180자 이내의 한국어 인사이트 텍스트
    """
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    data_summary = _format_market_data(market_data)

    user_prompt = f"""다음은 오늘 아침 한국·미국 시장 데이터입니다.

{data_summary}

위 데이터와 web_search 결과를 바탕으로 다음을 작성하세요:

1. 전일 한국·미국 시장의 핵심 뉴스 1개 (한 문장)
2. 오늘 시장에서 주목할 포인트 1개 (한 문장)

조건:
- 전체 분량은 한국어 180자 이내
- 두 문장을 한 단락으로 자연스럽게 이어 쓰세요
- 마크다운, 불릿, 헤더 사용 금지
- "투자 권유 아닙니다" 같은 면책 문구도 넣지 마세요 (별도로 처리됩니다)"""

    response = client.responses.create(
        model=config.OPENAI_MODEL,
        instructions=SYSTEM_INSTRUCTIONS,
        tools=[{"type": "web_search"}],
        input=user_prompt,
    )

    insight = (response.output_text or "").strip()

    if not insight:
        insight = "오늘 시황 인사이트 생성에 실패했습니다. 데이터만 확인하세요."

    return insight
