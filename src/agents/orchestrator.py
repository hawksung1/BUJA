from __future__ import annotations

"""
의도(intent) 감지 → 에이전트 선택 → 시스템 프롬프트 조합

에이전트 정의는 .claude/agents/*.md 에 있습니다.
Python 코드는 데이터 수집과 라우팅만 담당합니다.
"""

import re
from pathlib import Path

_AGENTS_DIR = Path(__file__).parent.parent.parent / ".claude" / "agents"

# 에이전트 파일 → 활성화 키워드 매핑
_INTENT_MAP: list[tuple[str, list[str]]] = [
    ("risk_officer", ["올인", "전액", "몰빵", "레버리지", "신용", "빚투", "대출투자"]),
    ("stock_analyst", []),   # 종목 감지는 별도 로직
    ("portfolio_manager", ["포트폴리오", "리밸런싱", "분석해줘", "비중", "자산배분", "내 주식"]),
    ("market_scout", ["시장", "뉴스", "이슈", "요즘", "최근", "오늘", "금리", "환율", "관세", "매크로", "거시"]),
]

_KOREAN_TICKERS: dict[str, str] = {
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
    "kodex200": "069500.KS", "tiger200": "102110.KS", "kodex나스닥100": "379800.KS",
    "tiger미국s&p500": "360750.KS", "kodex미국채10년": "308620.KS",
    "tiger미국채10년": "305080.KS", "kodex골드": "132030.KS",
}


def _load_agent(name: str) -> str:
    path = _AGENTS_DIR / f"{name}.md"
    try:
        raw = path.read_text(encoding="utf-8")
        # frontmatter 제거
        if raw.startswith("---"):
            parts = raw.split("---", 2)
            return parts[2].strip() if len(parts) >= 3 else raw
        return raw
    except FileNotFoundError:
        return ""


def detect_tickers(text: str) -> list[str]:
    found: list[str] = []
    text_lower = text.lower()
    for name, ticker in _KOREAN_TICKERS.items():
        if name in text_lower:
            found.append(ticker)
    for m in re.findall(r'\b([A-Z]{1,5}|[0-9]{6}\.(KS|KQ))\b', text.upper()):
        t = m[0] if isinstance(m, tuple) else m
        if t not in ("KS", "KQ"):
            found.append(t)
    return list(dict.fromkeys(found))[:3]


def needs_news(text: str) -> bool:
    return any(k in text for k in ["뉴스", "이슈", "시장", "요즘", "최근", "오늘", "호재", "악재", "관세", "금리", "환율", "매크로"])


def needs_youtube(text: str) -> bool:
    return any(k in text.lower() for k in ["머니코믹스", "유튜브", "youtube", "영상"])


def select_agents(user_message: str, has_portfolio: bool) -> list[str]:
    """메시지 의도에 맞는 에이전트 이름 목록 반환 (우선순위 순)."""
    selected: list[str] = []

    for agent_name, keywords in _INTENT_MAP:
        if agent_name == "stock_analyst":
            if detect_tickers(user_message):
                selected.append(agent_name)
        elif any(k in user_message for k in keywords):
            selected.append(agent_name)

    # 포트폴리오 있고 분석 요청이면 portfolio_manager 기본 포함
    if has_portfolio and not selected:
        selected.append("portfolio_manager")

    # 아무것도 안 잡히면 stock_analyst를 기본으로
    if not selected:
        selected.append("stock_analyst")

    # risk_officer는 항상 첫 번째로
    if "risk_officer" in selected:
        selected = ["risk_officer"] + [a for a in selected if a != "risk_officer"]

    return selected


def build_system_prompt(agents: list[str], philosophy: str) -> str:
    """선택된 에이전트 정의를 합쳐 시스템 프롬프트 구성."""
    parts = [
        "당신은 BUJA 어드바이저입니다. 아래 전문가 역할 정의에 따라 답변합니다.\n",
        f"## 투자 철학\n{philosophy}\n" if philosophy else "",
    ]
    for name in agents:
        content = _load_agent(name)
        if content:
            parts.append(content)

    return "\n\n---\n\n".join(p for p in parts if p)
