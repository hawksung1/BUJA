"""
Profile Page
"""
import streamlit as st

from src.middleware import auth_middleware
from src.services import UserService
from src.utils.async_helpers import run_async

st.set_page_config(
    page_title="Profile - BUJA",
    page_icon="👤",
    layout="centered"
)

# Authentication check
if not auth_middleware.is_authenticated():
    st.warning("Login required.")
    st.switch_page("pages/login.py")
    st.stop()

user = auth_middleware.get_current_user()
user_service = UserService()

# Render common sidebar
from src.utils.sidebar import render_sidebar

render_sidebar()

st.title("👤 Profile")

# Get user profile
try:
    user_with_profile = run_async(user_service.get_user_with_profile(user.id))
    profile = user_with_profile.profile
except Exception as e:
    st.error(f"Error retrieving profile: {str(e)}")
    profile = None

# Profile edit form
with st.form("profile_form"):
    st.subheader("Profile Information")
    name = st.text_input("Name", value=profile.name if profile else "")
    age = st.number_input("Age", min_value=1, max_value=120, value=profile.age if profile else None)
    occupation = st.text_input("Occupation", value=profile.occupation if profile else "")

    submit_button = st.form_submit_button("Update Profile", use_container_width=True)

    if submit_button:
        try:
            profile_data = {
                "name": name if name else None,
                "age": int(age) if age else None,
                "occupation": occupation if occupation else None,
            }
            run_async(user_service.update_profile(user.id, profile_data))
            st.success("Profile has been updated!")
            st.rerun()
        except Exception as e:
            st.error(f"Error updating profile: {str(e)}")

