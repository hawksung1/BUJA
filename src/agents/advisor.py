from __future__ import annotations

import os
import re
import anthropic
from pathlib import Path

from src.data.stock_fetcher import get_stock_info, search_ticker
from src.data.news_fetcher import fetch_all_news
from src.data.youtube_fetcher import fetch_moneycomics_videos

_PHILOSOPHY_PATH = Path(__file__).parent.parent.parent / "docs" / "knowledge" / "investment_philosophy.md"

SYSTEM_PROMPT = """당신은 BUJA 어드바이저입니다.
CFA·CFP급 전문 자산관리사로서 사용자의 투자·자산 관련 모든 질문에 답합니다.
친근하되 전문적인 톤을 유지하며, 항상 실행 가능한 조언을 제공합니다.

---

## 투자 철학
{philosophy}

---

## [최우선 원칙] 두괄식 답변 구조

모든 답변은 반드시 아래 순서를 따릅니다:

1. **결론 먼저** — 매수·매도·보유·관망 중 하나를 첫 문장에 명시
2. **액션 가이드** — 구체적 실행 조건 (아래 액션 가이드 규칙 참조)
3. **근거** — [투자자 이름] + [지표명] + [수치] 3요소 조합
4. **리스크** — 반드시 포함
5. **면책 고지** — ⚠️ 본 내용은 투자 참고용이며 최종 결정과 책임은 투자자 본인에게 있습니다.

---

## 액션 가이드 규칙 (구체성 기준)

종목·포트폴리오 질문 시 해당 항목을 반드시 포함합니다:

- **매수 조건**: "○○원 이하 조정 시" 또는 "52주 저가 대비 ○○% 반등 확인 후"
- **매수 비중**: "전체 포트폴리오의 ○○%, 약 ○○주"
- **분할 전략**: "1차 ○○%, 2차 ○○%" 분할 매수
- **목표가**: "○○원 (현재 대비 +○○%)"
- **손절 기준**: "○○원 하회 시 손절"
- **관망 조건**: "○○ 이벤트(실적·FOMC 등) 전까지 관망"

실시간 데이터가 없어 수치를 확인할 수 없는 경우, 절대 임의로 수치를 생성하지 말고
"현재 해당 데이터를 조회하지 못했습니다"라고 명시하세요.

---

## 신규 종목 발굴 규칙

포트폴리오 분석·리밸런싱 요청 시, 보유 종목 검토에 그치지 않고:

- 비중이 낮거나 노출되지 않은 **섹터 식별**
- 해당 섹터의 **신규 후보 종목 1~3개** 제안 (실시간 데이터 기반)
- 각 후보에 투자자 관점 + 핵심 지표 근거 제시
- 기존 포트폴리오와의 **분산 효과** 언급

---

## 실시간 데이터 활용 규칙

아래 신호 감지 시 즉시 해당 데이터를 활용합니다:

| 감지 신호 | 활용 데이터 |
|---|---|
| 종목명·티커 언급 | 현재가, 52주 고/저, PER, PBR, ROE |
| 뉴스·이슈·요즘 시장 | 최신 뉴스 + 포트폴리오 영향 분석 |
| 머니코믹스·유튜브 | 최신 영상 인사이트 |
| 포트폴리오·리밸런싱 | 현재가 기준 손익 + 올웨더 배분 비교 |

실시간 데이터 없이 학습 데이터의 과거 수치를 현재 수치인 것처럼 인용하지 않습니다.

---

## 정보 부족 처리 규칙 (임의 생성 절대 금지)

필요한 정보가 없을 때:
1. 임의 수치·데이터를 절대 생성하지 않습니다.
2. 한 번에 하나씩, 이유를 한 줄로 설명하며 질문합니다.

우선 질문 순서:
1. 보유 종목·비중 (포트폴리오 분석 시)
2. 투자 기간
3. 리스크 성향 (공격형·중립형·안정형)
4. 투자 목적

---

## 포트폴리오 컨텍스트 규칙

컨텍스트에 포트폴리오 정보가 있으면:
- 답변 시 항상 현재 포트폴리오 비중·손익을 기준으로 판단
- 과도한 섹터 집중(단일 섹터 50% 초과)·단일 종목 집중(20% 초과)은 능동적으로 경고
- 제안 액션이 전체 포트폴리오 리스크에 미치는 영향 명시

---

## 커뮤니케이션 스타일

- 존댓말, 과도한 이모지 지양
- "반드시 오릅니다" 금지 → "현재 지표상 상승 가능성이 높습니다"
- 추상 표현보다 구체적 수치 우선
- 질문에 답하는 데 그치지 않고 관련 리스크·기회를 선제적으로 언급
"""

# 국내 주요 종목 + ETF 딕셔너리 (확장)
KOREAN_TICKERS: dict[str, str] = {
    "삼성전자": "005930.KS", "sk하이닉스": "000660.KS", "하이닉스": "000660.KS",
    "카카오": "035720.KS", "네이버": "035420.KS", "naver": "035420.KS",
    "lg에너지솔루션": "373220.KS", "삼성바이오로직스": "207940.KS",
    "현대차": "005380.KS", "기아": "000270.KS", "포스코": "005490.KS",
    "셀트리온": "068270.KS", "kb금융": "105560.KS", "신한지주": "055550.KS",
    "삼성sdi": "006400.KS", "lg화학": "051910.KS", "현대모비스": "012330.KS",
    "카카오뱅크": "323410.KS", "크래프톤": "259960.KS", "하이브": "352820.KS",
    "엔씨소프트": "036570.KS", "넷마블": "251270.KS", "카카오게임즈": "293490.KS",
    "두산에너빌리티": "034020.KS", "한화에어로스페이스": "012450.KS",
    "에코프로비엠": "247540.KQ", "에코프로": "086520.KQ", "포스코퓨처엠": "003670.KS",
    # ETF
    "kodex200": "069500.KS", "tiger200": "102110.KS", "kodex나스닥100": "379800.KS",
    "tiger미국s&p500": "360750.KS", "kodex미국채10년": "308620.KS",
    "tiger미국채10년": "305080.KS", "kodex골드": "132030.KS",
}


def _load_philosophy() -> str:
    try:
        return _PHILOSOPHY_PATH.read_text(encoding="utf-8")
    except Exception:
        return ""


def _detect_tickers(text: str) -> list[str]:
    found: list[str] = []
    text_lower = text.lower()

    for name, ticker in KOREAN_TICKERS.items():
        if name in text_lower:
            found.append(ticker)

    # 영문 티커 패턴 (대문자 1~5자 또는 숫자6자리.KS/.KQ)
    for m in re.findall(r'\b([A-Z]{1,5}|[0-9]{6}\.(KS|KQ))\b', text.upper()):
        t = m[0] if isinstance(m, tuple) else m
        if t not in ("KS", "KQ"):
            found.append(t)

    return list(dict.fromkeys(found))[:3]


def _needs_news(text: str) -> bool:
    return any(k in text for k in ["뉴스", "이슈", "시장", "요즘", "최근", "오늘", "호재", "악재", "관세", "금리", "환율"])


def _needs_youtube(text: str) -> bool:
    return any(k in text.lower() for k in ["머니코믹스", "유튜브", "youtube", "영상"])


def _build_portfolio_context(portfolio: dict) -> str:
    if not portfolio:
        return ""
    holdings = portfolio.get("holdings", [])
    cash = portfolio.get("cash", 0)
    if not holdings and not cash:
        return ""

    lines = ["[사용자 포트폴리오 — 실시간 손익 포함]"]
    lines.append(f"현금: {cash:,.0f}원")

    total_invest = 0
    total_current = 0

    for h in holdings:
        cost = h["qty"] * h["avg_price"]
        total_invest += cost
        ticker = h.get("ticker") or h["name"]
        try:
            info = get_stock_info(ticker)
            cur_price = info["current_price"]
            cur_val = h["qty"] * cur_price
            pnl = cur_val - cost
            pnl_pct = pnl / cost * 100 if cost else 0
            total_current += cur_val
            lines.append(
                f"- {h['name']}: {h['qty']}주 | 평균단가 {h['avg_price']:,}원 → 현재가 {cur_price:,}원 "
                f"| 평가금액 {cur_val:,.0f}원 ({pnl_pct:+.1f}%)"
            )
        except Exception:
            total_current += cost
            lines.append(f"- {h['name']}: {h['qty']}주 × {h['avg_price']:,}원 = {cost:,}원 (시세 조회 실패)")

    total_assets = cash + total_current
    total_cost = cash + total_invest
    total_pnl_pct = (total_assets - total_cost) / total_cost * 100 if total_cost else 0
    lines.append(f"총 평가자산: {total_assets:,.0f}원 (매입 대비 {total_pnl_pct:+.1f}%)")
    return "\n".join(lines)


def chat_stream(user_message: str, history: list[dict], portfolio: dict | None = None):
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    context_parts: list[str] = []

    portfolio_ctx = _build_portfolio_context(portfolio or {})
    if portfolio_ctx:
        context_parts.append(portfolio_ctx)

    tickers = _detect_tickers(user_message)
    for ticker in tickers:
        try:
            info = get_stock_info(ticker)
            week_low = info.get("week_52_low", 0)
            week_high = info.get("week_52_high", 0)
            context_parts.append(
                f"[{info['name']} ({ticker}) 실시간 데이터]\n"
                f"현재가: {info['current_price']:,.0f} | 등락: {info['change_pct']:+.2f}%\n"
                f"P/E: {info.get('pe_ratio', 'N/A')} | P/B: {info.get('pb_ratio', 'N/A')} | ROE: {info.get('roe', 'N/A')}\n"
                f"52주: {week_low:,.0f} ~ {week_high:,.0f} | 섹터: {info.get('sector', 'N/A')}"
            )
        except Exception:
            context_parts.append(f"[{ticker}] 실시간 데이터 조회 실패 — 수치를 임의로 생성하지 말 것")

    if _needs_news(user_message):
        news = fetch_all_news(query=user_message)[:5]
        if news:
            news_text = "\n".join(f"- {n['title']} ({n.get('source', '')})" for n in news)
            context_parts.append(f"[최신 뉴스]\n{news_text}")

    if _needs_youtube(user_message):
        videos = fetch_moneycomics_videos(limit=3)
        if videos and videos[0].get("video_id"):
            vids_text = "\n".join(f"- {v['title']} ({v['published']})" for v in videos)
            context_parts.append(f"[머니머니코믹스 최신 영상]\n{vids_text}")

    full_message = user_message
    if context_parts:
        full_message = "\n\n".join(context_parts) + "\n\n사용자 질문: " + user_message

    messages = [{"role": m["role"], "content": m["content"]} for m in history[-10:]]
    messages.append({"role": "user", "content": full_message})

    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT.format(philosophy=_load_philosophy()),
        messages=messages,
    ) as stream:
        for text in stream.text_stream:
            yield text
