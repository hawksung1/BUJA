"""
BUJA Main Streamlit App
"""
import streamlit as st
from src.middleware import auth_middleware
from src.utils.async_helpers import run_async
from src.services import UserService
from src.repositories import UserRepository
from config.database import db
from config.logging import get_logger
from config.settings import settings

logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="BUJA - LLM-based Asset Management",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None  # Hide default menu
)

# Initialize admin user on first run
if "admin_initialized" not in st.session_state:
    async def init_admin():
        try:
            user_service = UserService()
            user_repo = UserRepository(db)
            admin_user = await user_repo.get_by_email("admin")
            if not admin_user:
                await user_service.register(
                    email="admin",
                    password="admin",
                    profile_data={
                        "name": "Administrator",
                        "occupation": "System Admin"
                    },
                    skip_validation=True  # Skip validation for admin account
                )
                logger.info("Admin user created successfully")
        except Exception as e:
            logger.warning(f"Admin initialization skipped: {e}")
    
    try:
        run_async(init_admin())
    except Exception as e:
        logger.warning(f"Admin initialization failed: {e}")
    
    st.session_state.admin_initialized = True

# Redirect to login if not authenticated, otherwise to chat
# Call get_current_user directly to check session state
user = auth_middleware.get_current_user()

# Auto login (for development environment)
if not user and settings.autologin:
    try:
        logger.info(f"Auto login enabled, attempting to login as {settings.autologin_email}")
        # Debug: check settings
        logger.debug(f"Autologin settings: enabled={settings.autologin}, email={settings.autologin_email}, password={'*' * len(settings.autologin_password)}")
        user = run_async(auth_middleware.login(settings.autologin_email, settings.autologin_password))
        if user:
            logger.info(f"Auto login successful: {user.email}")
            # Check session state
            logger.debug(f"Session state after autologin: user_id={st.session_state.get('user_id')}, user={st.session_state.get('user')}")
            # Short delay to ensure session state is saved before redirect
            import time
            time.sleep(0.1)
        else:
            logger.warning("Auto login returned None user")
    except Exception as e:
        logger.error(f"Auto login failed: {e}", exc_info=True)
        # In development environment, don't show error and redirect to login page
        if settings.environment == "development":
            logger.debug(f"Auto login failed, redirecting to login page: {e}")
        else:
            st.error(f"Auto login failed: {str(e)}")
elif user:
    logger.debug(f"User already authenticated: {user.email}")
elif not settings.autologin:
    logger.debug(f"Autologin is disabled (autologin={settings.autologin})")

if not user:
    st.switch_page("pages/login.py")
else:
    st.switch_page("pages/agent_chat.py")
