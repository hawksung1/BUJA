"""
Dashboard Page
"""
import streamlit as st
from src.middleware import auth_middleware
from src.services import PortfolioService, InvestmentPreferenceService, InvestmentService
from src.utils.async_helpers import run_async

st.set_page_config(
    page_title="Dashboard - BUJA",
    page_icon="📊",
    layout="wide"
)

# Authentication check
if not auth_middleware.is_authenticated():
    st.warning("Login required.")
    st.switch_page("pages/login.py")
    st.stop()

user = auth_middleware.get_current_user()

st.title(f"📊 Dashboard - {user.email if user else 'User'}")

# 공통 사이드바 렌더링
from src.utils.sidebar import render_sidebar
render_sidebar()

# Main content - Load actual data
try:
    portfolio_service = PortfolioService()
    preference_service = InvestmentPreferenceService()
    investment_service = InvestmentService()
    
    # Get portfolio summary
    try:
        portfolio_summary = run_async(portfolio_service.get_portfolio_summary(user.id))
        total_assets = portfolio_summary.get("total_value", 0)
        total_return = portfolio_summary.get("total_return", 0)
    except Exception:
        total_assets = 0
        total_return = 0
    
    # Get investment preference
    try:
        preference = run_async(preference_service.get_preference(user.id))
        risk_tolerance = f"{preference.risk_tolerance}/10" if preference else "Not Set"
    except Exception:
        risk_tolerance = "Not Set"
    
    # Get recent investments
    try:
        recent_investments = run_async(investment_service.get_investments(user.id, skip=0, limit=5))
    except Exception:
        recent_investments = []
    
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    total_assets = 0
    total_return = 0
    risk_tolerance = "Not Set"
    recent_investments = []

# Metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Assets", f"₩{total_assets:,.0f}", "0%")

with col2:
    st.metric("Total Return", f"{total_return:.2f}%", "0%")

with col3:
    st.metric("Risk Tolerance", risk_tolerance, "-")

st.markdown("---")

# Recent Activity
st.subheader("Recent Activity")
if recent_investments:
    for investment in recent_investments:
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{investment.asset_type}** - {investment.quantity} units")
            with col2:
                st.write(f"Buy Price: ₩{investment.buy_price:,.0f}")
            with col3:
                st.write(f"Date: {investment.buy_date}")
            st.divider()
else:
    st.info("No investment records yet. Add your first investment to get started!")

# Quick Actions
st.markdown("---")
st.subheader("Quick Actions")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📈 Set Investment Preference", use_container_width=True):
        st.switch_page("pages/investment_preference.py")

with col2:
    if st.button("🤖 Chat with Agent", use_container_width=True):
        st.switch_page("pages/agent_chat.py")

with col3:
    if st.button("👤 Update Profile", use_container_width=True):
        st.switch_page("pages/profile.py")

