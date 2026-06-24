"""
Google Gemini API를 사용해 시장 인사이트를 생성합니다.

시간대별 분기:
- KST 시각에 따라 7개 구간으로 나눠 각기 다른 초점의 프롬프트 사용
- 시황 텍스트 맨 앞에 시간대 라벨 포함 (예: "[07:23 장 시작 전 브리핑]")

503/429 등 일시적 오류에 대비한 강화된 폴백:
  1) gemini-2.5-flash 최대 3회 (5/15/30초 대기)
  2) gemini-2.5-flash-lite 최대 2회
  3) gemini-2.0-flash 최대 2회
  4) gemini-2.0-flash-lite 최대 2회
"""

import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from google import genai
from google.genai import types

from . import config


KST = ZoneInfo("Asia/Seoul")

SYSTEM_INSTRUCTION = """당신은 한국과 미국 주식 시장을 매 시간 브리핑하는 애널리스트입니다.
브리핑 시각과 시장 상태에 맞는 초점으로 작성하세요.
간결하고 객관적이며 사실 기반으로 작성하세요.
과장된 표현, 투자 권유, "반드시" "확실하다" 같은 단정적 표현은 피하세요.
주어진 뉴스 헤드라인에 없는 사실은 절대 만들어내지 마세요."""

MODEL_FALLBACK = [
    (config.GEMINI_MODEL, 3),
    ("gemini-2.5-flash-lite", 2),
    ("gemini-2.0-flash", 2),
    ("gemini-2.0-flash-lite", 2),
]

RETRY_DELAYS = [5, 15, 30]
RETRYABLE_KEYWORDS = ("503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED", "DEADLINE_EXCEEDED")


def _get_session(hour: int) -> dict:
    """KST 시간대(시 단위)에 따른 브리핑 컨텍스트 반환."""
    if 7 <= hour <= 8:
        return {
            "label": "장 시작 전 브리핑",
            "focus_lines": [
                "전일 미국 시장 마감 흐름과 핵심 뉴스 (2 문장)",
                "오늘 한국 시장 개장 전망과 주목할 변수 (1-2 문장)",
            ],
            "tone": "차분하고 준비된 톤, 오늘 하루를 시작하기 전 정리하는 느낌",
        }
    if 9 <= hour <= 10:
        return {
            "label": "개장 직후 브리핑",
            "focus_lines": [
                "한국 시장 개장 직후 지수·환율 흐름 (1-2 문장)",
                "오늘 주도하는 섹터나 종목, 주목 변수 (1-2 문장)",
            ],
            "tone": "역동적이고 즉각적인 톤, 변화 포착에 집중",
        }
    if 11 <= hour <= 12:
        return {
            "label": "오전장 정리",
            "focus_lines": [
                "오전 한국 시장의 핵심 흐름 정리 (2 문장)",
                "점심 이후 오후장에서 주목할 포인트 (1-2 문장)",
            ],
            "tone": "분석적이고 정리하는 톤",
        }
    if 13 <= hour <= 14:
        return {
            "label": "오후장 브리핑",
            "focus_lines": [
                "오후 한국 시장의 진행 상황 (1-2 문장)",
                "마감을 앞둔 변동 가능성과 주목 흐름 (1-2 문장)",
            ],
            "tone": "마감을 향해가는 긴장감 있는 톤",
        }
    if 15 <= hour <= 16:
        return {
            "label": "마감 브리핑",
            "focus_lines": [
                "오늘 한국 시장 마감 결과와 주요 흐름 (2 문장)",
                "오늘밤 미국 시장에서 주목할 이벤트와 일정 (1-2 문장)",
            ],
            "tone": "하루를 정리하고 다음을 예고하는 톤",
        }
    if 17 <= hour <= 21:
        return {
            "label": "장 후 분석",
            "focus_lines": [
                "오늘 한국 시장의 핵심 흐름과 의미 (2 문장)",
                "야간 미국 시장에서 주목할 변수와 한국에 미칠 영향 (1-2 문장)",
            ],
            "tone": "깊이 있는 분석 톤",
        }
    if hour == 22:
        return {
            "label": "미국 개장 직전 브리핑",
            "focus_lines": [
                "미국 시장 개장 직전 분위기와 주요 이슈 (2 문장)",
                "미국 개장 후 한국 ADR/관련 종목 동향 전망 (1-2 문장)",
            ],
            "tone": "미국 시장 개시를 앞둔 기대감 있는 톤",
        }
    # 새벽/그 외 시간대 폴백
    return {
        "label": "일반 시황",
        "focus_lines": [
            "현재 한국·미국 시장의 핵심 흐름 (2 문장)",
            "주목할 포인트와 변수 (1-2 문장)",
        ],
        "tone": "객관적인 톤",
    }


def _format_market_data(market_data: dict) -> str:
    """시장 데이터를 프롬프트용 텍스트로 정리."""
    lines = ["[지수·환율]"]
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


def _build_prompt(market_data: dict, news_text: str, session: dict, now_kst: datetime) -> str:
    """시간대 정보를 반영한 사용자 프롬프트 생성."""
    data_summary = _format_market_data(market_data)
    focus_text = "\n".join(
        f"{i+1}. {line}" for i, line in enumerate(session["focus_lines"])
    )

    return f"""현재 시각: {now_kst.strftime('%Y-%m-%d %H:%M')} (KST)
브리핑 종류: {session['label']}
톤 가이드: {session['tone']}

=== 시장 데이터 ===
{data_summary}

=== 뉴스 헤드라인 ===
{news_text}

위 정보를 바탕으로 다음 항목들을 한국어 한 단락으로 작성하세요:

{focus_text}

조건:
- 전체 분량은 한국어 350자 내외 (반드시 380자 이내)
- 마크다운, 불릿, 헤더, 번호 사용 금지
- 자연스럽게 이어지는 평문 단락으로 작성
- "투자 권유 아닙니다" 같은 면책 문구 넣지 말 것
- 뉴스 헤드라인에 없는 사실은 만들어내지 말 것
- 브리핑 종류와 톤 가이드에 맞춰 어조를 조정할 것"""


def _call_gemini(client, model: str, prompt: str) -> str:
    """Gemini API 단일 호출."""
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.4,
            max_output_tokens=1500,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
    return (response.text or "").strip()


def _is_retryable(error: Exception) -> bool:
    msg = str(error)
    return any(kw in msg for kw in RETRYABLE_KEYWORDS)


def generate_insight(market_data: dict, news_text: str) -> str:
    """
    현재 시간대에 맞는 시황 인사이트를 생성합니다.

    Returns:
        시간대 라벨을 헤더로 포함한 인사이트 텍스트.
        예: "[07:23 장 시작 전 브리핑]\\n전일 미국 시장은..."
    """
    now_kst = datetime.now(KST)
    session = _get_session(now_kst.hour)
    header = f"[{now_kst.strftime('%H:%M')} {session['label']}]"

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    user_prompt = _build_prompt(market_data, news_text, session, now_kst)

    last_error: Exception = RuntimeError("호출 시도 없음")

    for model, max_attempts in MODEL_FALLBACK:
        for attempt in range(1, max_attempts + 1):
            try:
                result = _call_gemini(client, model, user_prompt)
                if result:
                    if attempt > 1 or model != config.GEMINI_MODEL:
                        print(f"[insight] {model} (시도 {attempt}) 성공")
                    return f"{header}\n{result}"
                raise RuntimeError("Gemini가 빈 응답을 반환")

            except Exception as e:
                last_error = e
                error_msg = str(e)[:120]
                retryable = _is_retryable(e)
                is_last_attempt = attempt == max_attempts

                if retryable and not is_last_attempt:
                    delay = RETRY_DELAYS[min(attempt - 1, len(RETRY_DELAYS) - 1)]
                    print(
                        f"[insight] {model} 시도 {attempt} 실패 "
                        f"({error_msg}) → {delay}초 후 재시도"
                    )
                    time.sleep(delay)
                else:
                    print(f"[insight] {model} 시도 {attempt} 실패 ({error_msg})")
                    break

    raise RuntimeError(f"Gemini API 모든 재시도 실패: {last_error}")
