# 카카오톡 주식 브리핑 봇

매일 평일 아침 7:30 KST에 카카오톡 '나와의 채팅'으로 주식 시장 브리핑을 자동 발송합니다.

## 주요 기능

- 한국·미국 주요 지수 (KOSPI, KOSDAQ, S&P500, 나스닥, 다우)
- 관심 종목 가격·등락률 (config.py에서 자유롭게 설정)
- Claude AI가 웹 검색으로 작성한 시황 인사이트
- GitHub Actions로 100% 무료 자동 실행

## 메시지 예시

```
[06/06 주요 지수]
코스피 2,567.89 ▲0.45%
코스닥 745.12 ▼0.21%
S&P500 5,234.32 ▲0.78%
나스닥 16,234.50 ▲1.05%
다우 38,567.10 ▲0.32%
```

```
[관심 종목]
삼성전자 73,500 ▲0.68%
SK하이닉스 158,000 ▼1.25%
NAVER 195,500 ▲0.51%
Apple 189 ▲0.93%
NVIDIA 890 ▲2.10%
Tesla 245 ▼0.40%
```

```
[AI 시황]
연준의 금리 동결 발표 후 미 증시가 기술주 중심으로 상승했습니다.
오늘 한국 시장은 반도체 강세에 힘입어 양호한 출발이 예상됩니다.
```

## 셋업 가이드

### 1. API 키 발급

발급해야 할 키는 다음 3가지입니다.

**Anthropic API 키**
- https://console.anthropic.com 에서 발급
- 결제 수단 등록 필요 (Claude 사용량 종량제, 매일 1회 호출 시 월 1달러 미만)

**Kakao Developers 앱 생성**
1. https://developers.kakao.com 접속 후 로그인
2. [내 애플리케이션] > [애플리케이션 추가하기]
3. 생성 후 [앱 설정] > [플랫폼] > Web 플랫폼 추가
   - 사이트 도메인: `https://example.com`
4. [제품 설정] > [카카오 로그인] 활성화
   - Redirect URI 등록: `https://example.com/oauth`
5. [동의항목] > '카카오톡 메시지 전송' 활성화 (필수 동의 또는 선택 동의)
6. [앱 키] 메뉴에서 **REST API 키** 복사

### 2. Refresh Token 발급

로컬에서 한 번만 실행하면 됩니다.

```bash
git clone https://github.com/<your-username>/kakao-stock-bot.git
cd kakao-stock-bot
pip install -r requirements.txt
python scripts/get_kakao_token.py
```

스크립트 안내에 따라:
1. 출력된 인증 URL을 브라우저에서 열기
2. 카카오 로그인 + 동의
3. 리디렉트된 URL의 `code=` 다음 값을 복사해 입력
4. 출력된 `KAKAO_REFRESH_TOKEN` 값 보관 (다음 단계에서 사용)

Refresh Token 유효기간은 약 60일입니다.

### 3. GitHub Secrets 등록

깃허브 레포지토리 > Settings > Secrets and variables > Actions > New repository secret

| Name | Value |
|------|-------|
| `ANTHROPIC_API_KEY` | sk-ant-... |
| `KAKAO_REST_API_KEY` | (Kakao 앱 REST API 키) |
| `KAKAO_REFRESH_TOKEN` | (위 2단계에서 받은 값) |

### 4. 로컬 테스트 (선택)

`.env.example`을 복사해 `.env`로 만들고 값을 채운 뒤:

```bash
# .env 로드 후 실행 (직접 export 해도 됨)
export $(cat .env | xargs)

# 발송 없이 메시지만 콘솔에 출력
python -m src.main --dry-run

# 실제로 발송
python -m src.main
```

### 5. 자동 실행 시작

GitHub에 푸시하면 자동으로 매주 월~금 KST 07:30에 실행됩니다.

수동 실행: 레포지토리 > Actions 탭 > "Send Morning Stock Briefing" > "Run workflow"

## 관심 종목 변경

`src/config.py`의 `WATCHLIST_KR` / `WATCHLIST_US` 딕셔너리만 수정하면 됩니다.

```python
WATCHLIST_KR = {
    "삼성전자": "005930",
    "POSCO홀딩스": "005490",   # ← 추가
}

WATCHLIST_US = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",      # ← 추가
}
```

종목 코드 찾기:
- 한국: 6자리 단축코드 (KRX 또는 네이버 금융에서 확인)
- 미국: 티커 심볼 (Yahoo Finance에서 확인)

## 60일마다 해야 할 일

Refresh Token이 갱신되면 워크플로 로그에 `[WARNING] 새 Refresh Token이 발급되었습니다` 메시지와 함께 새 토큰이 출력됩니다. 이 값을 GitHub Secrets의 `KAKAO_REFRESH_TOKEN`에 덮어쓰면 됩니다.

(자동 갱신은 GitHub Token + PyGithub로 구현 가능하지만 보안 표면이 늘어나 MVP에서는 제외)

## 비용

- GitHub Actions: 퍼블릭 레포 무제한 / 프라이빗 월 2,000분 (사용량 ≈ 월 30분)
- Anthropic Claude: 일 1회 호출 ≈ 월 0.5~1 USD
- Kakao Open API: 무료

## 트러블슈팅

**"refresh token is invalid" 에러**
→ Refresh Token이 만료됐거나 잘못된 값. `scripts/get_kakao_token.py` 재실행.

**카카오 메시지가 도착하지 않음**
→ Kakao 앱의 [동의항목]에 '카카오톡 메시지 전송'이 켜져 있는지 확인.
→ Access Token 발급 시 `scope=talk_message`가 포함됐는지 확인.

**FinanceDataReader 에러**
→ 야후 파이낸스/네이버 금융 사이트 구조 변경 시 발생 가능. 라이브러리 최신 버전으로 업그레이드.

## 디렉토리 구조

```
kakao-stock-bot/
├── .github/workflows/
│   └── send_briefing.yml      # GitHub Actions 스케줄
├── scripts/
│   └── get_kakao_token.py     # 초기 OAuth 헬퍼
├── src/
│   ├── __init__.py
│   ├── config.py              # 종목 리스트 + 모델 설정
│   ├── stocks.py              # FinanceDataReader 래퍼
│   ├── insight.py             # Claude API 인사이트 생성
│   ├── kakao.py               # Kakao API (토큰 + 발송)
│   ├── formatter.py           # 메시지 포맷팅
│   └── main.py                # 파이프라인 진입점
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```
