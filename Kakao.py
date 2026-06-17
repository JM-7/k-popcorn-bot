"""
카카오 Open API: 토큰 갱신 + '나에게 보내기' 메시지 발송.

토큰 흐름:
1. Refresh Token으로 새 Access Token 발급 (매 실행)
2. Access Token으로 메시지 발송
3. Refresh Token도 함께 갱신되면 경고 출력 (GitHub Secret 수동 업데이트 필요)
"""

import json
import os
from typing import Optional

import requests

from . import config


TOKEN_URL = "https://kauth.kakao.com/oauth/token"
MEMO_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

# 카카오 텍스트 템플릿의 본문 글자수 제한
TEXT_TEMPLATE_MAX_LEN = 200


class KakaoClient:
    def __init__(
        self,
        rest_api_key: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ):
        self.rest_api_key = rest_api_key or os.environ["KAKAO_REST_API_KEY"]
        self.refresh_token = refresh_token or os.environ["KAKAO_REFRESH_TOKEN"]
        self.access_token: Optional[str] = None

    def refresh(self) -> None:
        """Refresh Token으로 새 Access Token을 발급받습니다."""
        response = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "client_id": self.rest_api_key,
                "refresh_token": self.refresh_token,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        self.access_token = data["access_token"]

        # Kakao는 Refresh Token 유효기간이 1개월 미만일 때만
        # 새 refresh_token을 함께 반환합니다.
        if "refresh_token" in data:
            new_refresh = data["refresh_token"]
            print("=" * 60)
            print("[WARNING] 새 Refresh Token이 발급되었습니다.")
            print("GitHub Secrets의 KAKAO_REFRESH_TOKEN을 아래 값으로 갱신하세요:")
            print(new_refresh)
            print("=" * 60)

    def send_text(self, text: str, link_url: Optional[str] = None) -> dict:
        """
        '나에게 보내기'로 텍스트 메시지를 발송합니다.
        200자를 초과하면 자동으로 잘립니다.
        """
        if self.access_token is None:
            raise RuntimeError("먼저 refresh()를 호출하세요.")

        if len(text) > TEXT_TEMPLATE_MAX_LEN:
            text = text[: TEXT_TEMPLATE_MAX_LEN - 1] + "…"

        link = link_url or config.DEFAULT_LINK_URL
        template = {
            "object_type": "text",
            "text": text,
            "link": {
                "web_url": link,
                "mobile_web_url": link,
            },
            "button_title": "자세히 보기",
        }

        response = requests.post(
            MEMO_URL,
            headers={"Authorization": f"Bearer {self.access_token}"},
            data={"template_object": json.dumps(template, ensure_ascii=False)},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def send_messages(self, messages: list) -> None:
        """여러 메시지를 순서대로 발송합니다."""
        for i, msg in enumerate(messages, 1):
            try:
                self.send_text(msg)
                print(f"[kakao] {i}/{len(messages)} 메시지 발송 완료 ({len(msg)}자)")
            except Exception as e:
                print(f"[kakao] {i}/{len(messages)} 발송 실패: {e}")
                raise
