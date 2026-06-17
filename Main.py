"""
파이프라인 진입점.

흐름:
  1. config의 지수·관심종목 데이터 수집 (FinanceDataReader)
  2. Claude API로 시황 인사이트 생성 (web_search 포함)
  3. 메시지 3개로 포맷팅
  4. 카카오톡 '나에게 보내기'로 발송

실행:
  python -m src.main
  python -m src.main --dry-run    # 발송하지 않고 콘솔에만 출력
"""

import sys

from . import config
from . import formatter
from . import insight
from . import stocks
from .kakao import KakaoClient


def run(dry_run: bool = False) -> int:
    # 1. 데이터 수집
    print("[1/4] 시장 데이터 수집 중...")
    all_indices = {**config.INDICES_KR, **config.INDICES_US}
    all_watchlist = {**config.WATCHLIST_KR, **config.WATCHLIST_US}
    market_data = stocks.collect_all(all_indices, all_watchlist)
    print(
        f"      지수 {len(market_data['indices'])}개, "
        f"종목 {len(market_data['stocks'])}개 수집"
    )

    # 2. 인사이트 생성
    print("[2/4] Claude로 시황 인사이트 생성 중...")
    try:
        insight_text = insight.generate_insight(market_data)
        print(f"      생성 완료 ({len(insight_text)}자)")
    except Exception as e:
        print(f"      실패: {e}")
        insight_text = "AI 인사이트 생성에 실패했습니다."

    # 3. 메시지 조립
    print("[3/4] 메시지 포맷팅...")
    messages = formatter.build_all_messages(market_data, insight_text)
    for i, m in enumerate(messages, 1):
        print(f"      --- 메시지 {i} ({len(m)}자) ---")
        print(m)
        print()

    # 4. 발송
    if dry_run:
        print("[4/4] --dry-run: 발송 생략")
        return 0

    print("[4/4] 카카오톡 발송 중...")
    client = KakaoClient()
    client.refresh()
    client.send_messages(messages)
    print("완료.")
    return 0


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    return run(dry_run=dry_run)


if __name__ == "__main__":
    sys.exit(main())
