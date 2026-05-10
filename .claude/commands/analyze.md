# /analyze — 종목 심층 분석

주어진 종목($ARGUMENTS)에 대해 `stock_analyst` 에이전트를 호출하여 5대 투자자 기준 심층 분석을 수행합니다.

## 프로세스

1. yfinance로 실시간 데이터 수집 (현재가·P/E·P/B·ROE·부채비율·FCF·52주 고저·섹터)
2. 최근 7일 관련 뉴스 Top 5 수집 후 센티먼트 분류
3. `stock_analyst` 에이전트에 `[STOCK_DATA]`·`[USER_PORTFOLIO]`·`[RISK_PROFILE]` 주입하여 분석 실행
4. 출력 형식은 `stock_analyst` 에이전트 정의를 따름
