"""
Google Gemini API를 사용해 시장 인사이트를 생성합니다.
RSS에서 수집한 뉴스 헤드라인과 시장 데이터를 함께 LLM에 전달해,
"전일 핵심 뉴스 + 오늘 시장 포인트"를 한 단락으로 요약합니다.

503/429 등 일시적 오류에 대비해 지수 백오프 재시도와 모델 폴백을 적용:
  1) 메인 모델 최대 3회 재시도 (5초, 10초, 20초 대기)
  2) 모두 실패 시 더 가벼운 라이트 모델로 폴백 (최대 2회 재시도)
"""

import os
import time

from google import genai
from google.genai import types

from . import config


SYSTEM_INSTRUCTION = """당신은 한국과 미국 주식 시장을 매일 아침 브리핑하는 애널리스트입니다.
간결하고 객관적이며 사실 기반으로 작성하세요.
과장된 표현, 투자 권유, "반드시" "확실하다" 같은 단정적 표현은 피하세요.
주어진 뉴스 헤드라인에 없는 사실은 절대 만들어내지 마세요."""

# 폴백 순서: (모델명, 최대 시도 횟수)
# 503 다발 시간대에는 라이트 모델이 더 안정적입니다.
MODEL_FALLBACK = [
    (config.GEMINI_MODEL, 3),
    ("gemini-2.5-flash-lite", 2),
]

# 재시도 트리거가 되는 에러 키워드
RETRYABLE_KEYWORDS = ("503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED", "DEADLINE_EXCEEDED")


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


def _call_gemini(client, model: str, prompt: str) -> str:
    """Gemini API 단일 호출. 성공 시 텍스트 반환."""
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.4,
            max_output_tokens=8000,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
    return (response.text or "").strip()


def _is_retryable(error: Exception) -> bool:
    """일시적 오류인지 판별."""
    msg = str(error)
    return any(kw in msg for kw in RETRYABLE_KEYWORDS)


def generate_insight(market_data: dict, news_text: str) -> str:
    """
    시장 데이터 + RSS 뉴스를 바탕으로 한국어 시황 인사이트를 생성합니다.

    Args:
        market_data: stocks.collect_all()의 반환값
        news_text:   news.format_news_for_prompt()의 반환값

    Returns:
        한국어 인사이트 텍스트 (150자 내외)

    Raises:
        모든 재시도가 실패하면 마지막 예외를 raise (상위에서 처리)
    """
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    data_summary = _format_market_data(market_data)
    user_prompt = f"""다음은 오늘 아침 시장 데이터와 전일 뉴스 헤드라인입니다.

=== 시장 데이터 ===
{data_summary}

=== 뉴스 헤드라인 ===
{news_text}

위 정보를 바탕으로 다음을 한국어 한 단락으로 작성하세요:

1. 전일 한국 시장 핵심 흐름 + 관련 뉴스 (2-3 문장)
2. 전일 미국 시장 핵심 흐름 + 관련 뉴스 (2-3 문장)
3. 오늘 시장에서 주목할 포인트 (1-2 문장)

조건:
- 전체 분량은 한국어 350자 내외 (반드시 380자 이내)
- 마크다운, 불릿, 헤더, 번호 사용 금지
- 자연스럽게 이어지는 평문 단락들로 작성
- 단락 사이는 줄바꿈 1번
- "투자 권유 아닙니다" 같은 면책 문구 넣지 말 것
- 뉴스 헤드라인에 없는 사실은 만들어내지 말 것"""

    last_error: Exception = RuntimeError("호출 시도 없음")

    for model, max_attempts in MODEL_FALLBACK:
        for attempt in range(1, max_attempts + 1):
            try:
                result = _call_gemini(client, model, user_prompt)
                if result:
                    if attempt > 1 or model != config.GEMINI_MODEL:
                        print(f"[insight] {model} (시도 {attempt}) 성공")
                    return result
                # 빈 응답도 재시도 대상
                raise RuntimeError("Gemini가 빈 응답을 반환")

            except Exception as e:
                last_error = e
                error_msg = str(e)[:120]
                retryable = _is_retryable(e)
                is_last_attempt = attempt == max_attempts

                if retryable and not is_last_attempt:
                    delay = 5 * (2 ** (attempt - 1))  # 5, 10, 20초
                    print(
                        f"[insight] {model} 시도 {attempt} 실패 "
                        f"({error_msg}) → {delay}초 후 재시도"
                    )
                    time.sleep(delay)
                else:
                    # 영구 오류이거나 이 모델의 마지막 시도
                    print(
                        f"[insight] {model} 시도 {attempt} 실패 ({error_msg})"
                    )
                    break  # 다음 폴백 모델로

    # 모든 모델·시도 실패
    raise RuntimeError(f"Gemini API 모든 재시도 실패: {last_error}")
