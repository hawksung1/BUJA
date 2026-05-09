import json
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="BUJA 어드바이저",
    page_icon="💰",
    layout="wide",
)

# --- API 키 검증 ---
if not os.getenv("ANTHROPIC_API_KEY"):
    st.error("ANTHROPIC_API_KEY가 설정되지 않았습니다.")
    st.markdown("""
    **해결 방법:**
    1. 프로젝트 루트에 `.env` 파일을 생성하세요.
    2. 아래 내용을 추가하세요:
    ```
    ANTHROPIC_API_KEY=sk-ant-api03-...
    ```
    3. API 키 발급: [console.anthropic.com](https://console.anthropic.com) → API Keys
    """)
    st.stop()

# --- 세션 초기화 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {"cash": 0, "holdings": []}

# --- 사이드바 ---
with st.sidebar:
    st.title("💰 BUJA")
    st.divider()

    tab_port, tab_ex = st.tabs(["내 포트폴리오", "예시"])

    with tab_port:
        st.caption("API 연동 없이 직접 입력하세요")

        cash = st.number_input(
            "현금 (원)",
            min_value=0,
            value=st.session_state.portfolio["cash"],
            step=100000,
            format="%d",
        )

        st.markdown("**보유 종목**")
        holdings = st.session_state.portfolio["holdings"].copy()

        to_remove = []
        for i, h in enumerate(holdings):
            cols = st.columns([3, 1])
            with cols[0]:
                st.caption(f"{h['name']} {h['qty']}주 @ {h['avg_price']:,}원")
            with cols[1]:
                if st.button("✕", key=f"del_{i}"):
                    to_remove.append(i)
        for i in reversed(to_remove):
            holdings.pop(i)

        with st.expander("+ 종목 추가"):
            new_name = st.text_input("종목명 또는 티커", placeholder="삼성전자 / 005930.KS / AAPL")
            new_qty = st.number_input("수량 (주)", min_value=1, value=1, step=1)
            new_avg = st.number_input("평균단가 (원/$)", min_value=0, value=0, step=100, format="%d")
            if st.button("추가", use_container_width=True):
                if new_name:
                    holdings.append({"name": new_name, "qty": new_qty, "avg_price": new_avg})

        if st.button("저장", type="primary", use_container_width=True):
            st.session_state.portfolio = {"cash": cash, "holdings": holdings}
            st.success("저장됨")
            st.rerun()

        # 포트폴리오 요약
        if st.session_state.portfolio["holdings"] or st.session_state.portfolio["cash"]:
            st.divider()
            total_invest = sum(h["qty"] * h["avg_price"] for h in st.session_state.portfolio["holdings"])
            total_assets = st.session_state.portfolio["cash"] + total_invest
            st.metric("총 자산 (매입가)", f"{total_assets:,.0f}원")
            if total_assets > 0:
                cash_r = st.session_state.portfolio["cash"] / total_assets * 100
                st.caption(f"현금 {cash_r:.0f}% | 주식 {100 - cash_r:.0f}%")

        # JSON 백업/복원
        st.divider()
        st.caption("포트폴리오 백업")
        col_a, col_b = st.columns(2)
        with col_a:
            pf_json = json.dumps(st.session_state.portfolio, ensure_ascii=False, indent=2)
            st.download_button("내보내기", data=pf_json, file_name="buja_portfolio.json", mime="application/json", use_container_width=True)
        with col_b:
            uploaded = st.file_uploader("불러오기", type="json", label_visibility="collapsed")
            if uploaded:
                try:
                    loaded = json.load(uploaded)
                    st.session_state.portfolio = loaded
                    st.success("복원됨")
                    st.rerun()
                except Exception:
                    st.error("파일 형식 오류")

    with tab_ex:
        examples = [
            "삼성전자 지금 사도 돼?",
            "NVDA 고평가야?",
            "내 포트폴리오 분석해줘",
            "리밸런싱 추천해줘",
            "IT 비중 높은데 다른 섹터 추천해줘",
            "요즘 시장 어때?",
            "머니코믹스 최신 영상 뭐야?",
            "워런 버핏이라면 지금 어떻게 할까?",
        ]
        for ex in examples:
            if st.button(ex, use_container_width=True, key=f"ex_{ex}"):
                st.session_state.messages.append({"role": "user", "content": ex})
                st.rerun()

    st.divider()
    if st.button("대화 초기화", use_container_width=True):
        if st.session_state.get("confirm_clear"):
            st.session_state.messages = []
            st.session_state.confirm_clear = False
            st.rerun()
        else:
            st.session_state.confirm_clear = True
            st.warning("한 번 더 누르면 초기화됩니다.")

# --- 메인 채팅 ---
st.title("BUJA 어드바이저")
st.caption("워런 버핏 · 그레이엄 · 피터 린치 · 레이 달리오 · 필립 피셔 기반 AI 자산관리사")

if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "안녕하세요! BUJA 어드바이저입니다.\n\n"
            "왼쪽 사이드바에 보유 현금과 종목을 입력하면 **현재가 기준 손익**과 함께 분석해드립니다. "
            "API 연동 없이도 바로 사용 가능합니다.\n\n"
            "**예시**\n"
            "- 삼성전자 지금 사도 돼?\n"
            "- 내 포트폴리오 분석해줘\n"
            "- IT 비중 높은데 다른 섹터 추천해줘\n"
            "- 요즘 시장 어때?"
        ),
    })

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("종목, 시장, 포트폴리오 등 무엇이든 물어보세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        from src.agents.advisor import chat_stream
        placeholder = st.empty()
        full = ""
        for chunk in chat_stream(prompt, st.session_state.messages[:-1], portfolio=st.session_state.portfolio):
            full += chunk
            placeholder.markdown(full)

    st.session_state.messages.append({"role": "assistant", "content": full})
