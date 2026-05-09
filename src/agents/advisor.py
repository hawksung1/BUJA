from __future__ import annotations

"""
advisor.py — 스트리밍 래퍼

분석 로직은 .claude/agents/*.md 에 정의된 에이전트가 담당합니다.
이 파일은 데이터 수집 → 에이전트 선택 → Claude 스트리밍 호출만 합니다.
"""

import os
import anthropic
from pathlib import Path

from src.agents.orchestrator import (
    select_agents,
    build_system_prompt,
    detect_tickers,
    needs_news,
    needs_youtube,
)
from src.data.stock_fetcher import get_stock_info
from src.data.news_fetcher import fetch_all_news
from src.data.youtube_fetcher import fetch_moneycomics_videos

_PHILOSOPHY_PATH = Path(__file__).parent.parent.parent / "docs" / "knowledge" / "investment_philosophy.md"


def _load_philosophy() -> str:
    try:
        return _PHILOSOPHY_PATH.read_text(encoding="utf-8")
    except Exception:
        return ""


def _collect_context(user_message: str, portfolio: dict) -> list[str]:
    parts: list[str] = []

    # 포트폴리오 컨텍스트
    holdings = portfolio.get("holdings", [])
    cash = portfolio.get("cash", 0)
    risk_profile = portfolio.get("risk_profile", "")

    if holdings or cash:
        lines = ["[USER_PORTFOLIO]"]
        if risk_profile:
            lines.append(f"리스크 성향: {risk_profile}")
        lines.append(f"현금: {cash:,.0f}원")
        total_invest = total_current = 0
        for h in holdings:
            cost = h["qty"] * h["avg_price"]
            total_invest += cost
            try:
                info = get_stock_info(h.get("ticker") or h["name"])
                cur_price = info["current_price"]
                cur_val = h["qty"] * cur_price
                pnl_pct = (cur_val - cost) / cost * 100 if cost else 0
                total_current += cur_val
                lines.append(
                    f"- {h['name']}: {h['qty']}주 | 평균단가 {h['avg_price']:,}원 → "
                    f"현재가 {cur_price:,}원 | 평가 {cur_val:,.0f}원 ({pnl_pct:+.1f}%)"
                )
            except Exception:
                total_current += cost
                lines.append(f"- {h['name']}: {h['qty']}주 × {h['avg_price']:,}원 (시세 조회 실패)")

        total_assets = cash + total_current
        total_cost = cash + total_invest
        pnl_total = (total_assets - total_cost) / total_cost * 100 if total_cost else 0
        lines.append(f"총 평가자산: {total_assets:,.0f}원 (매입 대비 {pnl_total:+.1f}%)")
        parts.append("\n".join(lines))

    # 종목 실시간 데이터
    for ticker in detect_tickers(user_message):
        try:
            info = get_stock_info(ticker)
            w_low = info.get("week_52_low") or 0
            w_high = info.get("week_52_high") or 0
            cur = info["current_price"]
            pos_pct = ((cur - w_low) / (w_high - w_low) * 100) if w_high > w_low else None

            roe_val = info.get("roe")
            roe_str = f"{roe_val*100:.1f}%" if roe_val else "N/A"
            de_val = info.get("debt_to_equity")
            de_str = f"{de_val:.1f}%" if de_val else "N/A"
            fcf_val = info.get("free_cashflow")
            fcf_str = f"{fcf_val/1e8:+.0f}억" if fcf_val else "N/A"
            gn = info.get("graham_number")
            gn_str = f"{gn:,.0f} (안전마진 {(gn-cur)/gn*100:+.1f}%)" if gn and cur else "N/A"
            peg_str = str(info.get("peg_ratio", "N/A"))
            op_str = f"{info.get('operating_margin',0)*100:.1f}%" if info.get("operating_margin") else "N/A"
            pos_str = f"저점 대비 {pos_pct:.0f}% 위치" if pos_pct is not None else "N/A"

            parts.append(
                f"[STOCK_DATA: {info['name']} ({ticker})]\n"
                f"현재가: {cur:,.0f}원 | 등락: {info['change_pct']:+.2f}%\n"
                f"52주: {w_low:,.0f} ~ {w_high:,.0f} | {pos_str}\n"
                f"--- 그레이엄 지표 ---\n"
                f"P/E: {info.get('pe_ratio', 'N/A')}배 (기준 <15) | P/B: {info.get('pb_ratio', 'N/A')}배 (기준 <1.5)\n"
                f"Graham Number: {gn_str} | 부채비율 D/E: {de_str} (기준 <50%)\n"
                f"--- 버핏 지표 ---\n"
                f"ROE: {roe_str} (기준 >15%) | 영업이익률: {op_str} (기준 >20%) | FCF: {fcf_str}\n"
                f"--- 린치 지표 ---\n"
                f"PEG: {peg_str} (기준 <1.0 이상적) | 섹터: {info.get('sector', 'N/A')}\n"
                f"--- 피셔 지표 ---\n"
                f"매출성장률: {info.get('revenue_growth', 'N/A')} | EPS성장률: {info.get('earnings_growth', 'N/A')}"
            )
        except Exception:
            parts.append(f"[STOCK_DATA: {ticker}] 조회 실패 — 임의 수치 생성 금지")

    # 뉴스
    if needs_news(user_message):
        news = fetch_all_news(query=user_message)[:5]
        if news:
            parts.append("[NEWS]\n" + "\n".join(f"- {n['title']} ({n.get('source', '')})" for n in news))

    # 유튜브
    if needs_youtube(user_message):
        videos = fetch_moneycomics_videos(limit=3)
        if videos and videos[0].get("video_id"):
            parts.append("[YOUTUBE]\n" + "\n".join(f"- {v['title']} ({v['published']})" for v in videos))

    return parts


def chat_stream(user_message: str, history: list[dict], portfolio: dict | None = None):
    portfolio = portfolio or {}
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    has_portfolio = bool(portfolio.get("holdings") or portfolio.get("cash"))
    agents = select_agents(user_message, has_portfolio)

    context_parts = _collect_context(user_message, portfolio)
    full_message = user_message
    if context_parts:
        full_message = "\n\n".join(context_parts) + "\n\n사용자 질문: " + user_message

    messages = [{"role": m["role"], "content": m["content"]} for m in history[-10:]]
    messages.append({"role": "user", "content": full_message})

    philosophy = _load_philosophy()
    system_text = build_system_prompt(agents, philosophy)

    system_content = [{"type": "text", "text": system_text, "cache_control": {"type": "ephemeral"}}]

    try:
        with client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=system_content,
            messages=messages,
            betas=["prompt-caching-2024-07-31"],
        ) as stream:
            for text in stream.text_stream:
                yield text
    except Exception:
        with client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=system_text,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                yield text
