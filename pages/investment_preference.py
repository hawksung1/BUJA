"""
Investment Preference Page
"""
import streamlit as st
from src.middleware import auth_middleware
from src.services import InvestmentPreferenceService
from src.exceptions import ValidationError
from src.utils.async_helpers import run_async

st.set_page_config(
    page_title="Investment Preference - BUJA",
    page_icon="📈",
    layout="wide"
)

# Authentication check
if not auth_middleware.is_authenticated():
    st.warning("Login required.")
    st.switch_page("pages/login.py")
    st.stop()

user = auth_middleware.get_current_user()
preference_service = InvestmentPreferenceService()

# 공통 사이드바 렌더링
from src.utils.sidebar import render_sidebar
render_sidebar()

st.title("📈 Investment Preference")

# Get current preference
try:
    preference = run_async(preference_service.get_preference(user.id))
except Exception as e:
    preference = None
    if "not found" not in str(e).lower():
        st.error(f"Error loading preference: {str(e)}")

# Preference form
with st.form("preference_form"):
    st.subheader("Risk Tolerance")
    risk_tolerance = st.slider(
        "Risk Tolerance (1-10)",
        min_value=1,
        max_value=10,
        value=preference.risk_tolerance if preference else 5,
        help="1 = Very Conservative, 10 = Very Aggressive"
    )
    
    st.subheader("Investment Goals")
    target_return = st.number_input(
        "Target Return (%)",
        min_value=0.0,
        max_value=100.0,
        value=float(preference.target_return) if preference and preference.target_return else 7.0,
        step=0.1
    )
    
    investment_period = st.selectbox(
        "Investment Period",
        options=["SHORT", "MEDIUM", "LONG"],
        index=0 if not preference else ["SHORT", "MEDIUM", "LONG"].index(preference.investment_period) if preference.investment_period in ["SHORT", "MEDIUM", "LONG"] else 0
    )
    
    investment_experience = st.selectbox(
        "Investment Experience",
        options=["BEGINNER", "INTERMEDIATE", "ADVANCED"],
        index=0 if not preference else ["BEGINNER", "INTERMEDIATE", "ADVANCED"].index(preference.investment_experience) if preference.investment_experience in ["BEGINNER", "INTERMEDIATE", "ADVANCED"] else 0
    )
    
    st.subheader("Risk Management")
    max_loss_tolerance = st.number_input(
        "Max Loss Tolerance (%)",
        min_value=0.0,
        max_value=100.0,
        value=float(preference.max_loss_tolerance) if preference and preference.max_loss_tolerance else 20.0,
        step=0.1,
        help="Maximum acceptable loss percentage"
    )
    
    submit_button = st.form_submit_button("Save Preference", use_container_width=True)
    
    if submit_button:
        try:
            preference_data = {
                "risk_tolerance": risk_tolerance,
                "target_return": target_return,
                "investment_period": investment_period,
                "investment_experience": investment_experience,
                "max_loss_tolerance": max_loss_tolerance,
            }
            
            import asyncio
            updated_preference = run_async(
                preference_service.update_preference(user.id, preference_data)
            )
            st.success("Preference updated successfully!")
            st.rerun()
        except ValidationError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Error updating preference: {str(e)}")

# Show current preference summary
if preference:
    st.markdown("---")
    st.subheader("Current Preference Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Risk Tolerance", f"{preference.risk_tolerance}/10")
    
    with col2:
        st.metric("Target Return", f"{preference.target_return}%")
    
    with col3:
        st.metric("Investment Period", preference.investment_period)

