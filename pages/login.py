"""
Login and Registration Page
"""
import streamlit as st
from src.middleware import auth_middleware
from src.services import UserService
from src.exceptions import InvalidCredentialsError, ValidationError, UserAlreadyExistsError
from config.logging import get_logger

logger = get_logger(__name__)

st.set_page_config(
    page_title="Login - BUJA",
    page_icon="🔐",
    layout="centered"
)

user_service = UserService()

# Auto login 체크 (app.py에서 처리되지 않은 경우 대비)
from config.settings import settings
user = auth_middleware.get_current_user()

if not user and settings.autologin:
    try:
        logger.info(f"Auto login from login page, attempting to login as {settings.autologin_email}")
        from src.utils.async_helpers import run_async
        user = run_async(auth_middleware.login(settings.autologin_email, settings.autologin_password))
        if user:
            logger.info(f"Auto login successful: {user.email}")
            st.switch_page("pages/agent_chat.py")
            st.stop()
    except Exception as e:
        logger.warning(f"Auto login failed in login page: {e}")

# Render common sidebar (execute first to apply CSS)
from src.utils.sidebar import render_sidebar
render_sidebar()

# Already logged in - redirect to chat
if auth_middleware.is_authenticated():
    st.switch_page("pages/agent_chat.py")
    st.stop()

# Tabs for Login and Register
tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

# Login Tab
with tab1:
    st.title("🔐 Login")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit_button = st.form_submit_button("Login", use_container_width=True)
        
        if submit_button:
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                try:
                    from src.utils.async_helpers import run_async
                    from config.database import db
                    
                    logger.info(f"Login attempt for email: {email}")
                    
                    # Check if database is available
                    if not db.engine or not db.session_factory:
                        st.error("❌ Database Connection Error")
                        st.markdown("**Database has not been initialized.**")
                        
                        # Display diagnostic information
                        with st.expander("🔍 Diagnostic Information", expanded=True):
                            # Check database driver
                            from config.settings import settings
                            is_sqlite = "sqlite" in settings.database_url.lower()
                            
                            if is_sqlite:
                                try:
                                    import aiosqlite
                                    st.success(f"✅ aiosqlite installed (SQLite available)")
                                except ImportError:
                                    st.error("❌ aiosqlite is not installed.")
                                    st.code("pip install aiosqlite", language="bash")
                            else:
                                try:
                                    import asyncpg
                                    st.success(f"✅ asyncpg installed (version: {asyncpg.__version__})")
                                except ImportError:
                                    st.error("❌ asyncpg is not installed.")
                                    st.code("uv pip install asyncpg\n# or\npip install asyncpg", language="bash")
                                    st.info("💡 Tip: Using SQLite allows you to use the app without Docker!")
                            
                            # Check database URL
                            from config.settings import settings
                            masked_url = settings.database_url.replace("://", "://***:***@") if "@" in settings.database_url else settings.database_url
                            st.info(f"📋 Database URL: `{masked_url}`")
                            
                            # Solution
                            st.markdown("### Solution:")
                            
                            # Check database type
                            is_sqlite = "sqlite" in settings.database_url.lower()
                            
                            if is_sqlite:
                                st.markdown("""
                                **Using SQLite** (Docker not required):
                                1. **Install aiosqlite**:
                                   ```bash
                                   pip install aiosqlite
                                   ```
                                2. **Check data directory**: `data/` folder will be created automatically
                                3. **Run migration**:
                                   ```bash
                                   alembic upgrade head
                                   ```
                                
                                SQLite can be used immediately without installing a separate server!
                                """)
                            else:
                                st.markdown("""
                                1. **Install asyncpg** (run the command above)
                                2. **Start PostgreSQL**:
                                   ```bash
                                   docker-compose -f docker-compose.local.yml up -d postgres
                                   ```
                                3. **Create .env.local file** (in project root):
                                   ```env
                                   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/buja_local
                                   ```
                                4. **Run migration**:
                                   ```bash
                                   alembic upgrade head
                                   ```
                                
                                Or to switch to SQLite, add the following to `.env.local`:
                                ```env
                                DATABASE_URL=sqlite+aiosqlite:///./data/buja.db
                                ```
                                """)
                            
                            st.markdown("For more details, see `docs/LOGIN_TROUBLESHOOTING.md` or `SETUP_DATABASE.md`.")
                        st.stop()
                    
                    logger.debug(f"Attempting login for: {email}")
                    user = run_async(auth_middleware.login(email, password))
                    if user:
                        # Verify session state is saved
                        logger.info(f"Login successful for user: {user.email}, user_id: {user.id}")
                        logger.debug(f"Session state after login: user_id={st.session_state.get('user_id')}, user={st.session_state.get('user')}")
                        # Display success message
                        st.success(f"✅ Login successful! Welcome, {user.email}.")
                        # Redirect
                        import time
                        time.sleep(0.5)  # Short delay so user can see the message
                        st.switch_page("pages/agent_chat.py")
                    else:
                        logger.warning(f"Login returned None for email: {email}")
                        st.error("Login failed: User not found")
                except InvalidCredentialsError as e:
                    logger.warning(f"Invalid credentials for email: {email}, error: {str(e)}")
                    st.error(f"❌ Login failed: {str(e)}")
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Login exception for email {email}: {error_msg}", exc_info=True)
                    if "Database" in error_msg or "asyncpg" in error_msg or "connection" in error_msg.lower():
                        st.error("❌ Database Connection Error")
                        st.info("Solution: 1) Install asyncpg: `uv pip install asyncpg`, 2) Start database: `docker-compose up -d postgres`")
                    else:
                        st.error(f"❌ Login error: {error_msg}")
                        st.exception(e)  # Display detailed error information

# Register Tab
with tab2:
    st.title("📝 Register")
    
    with st.form("register_form"):
        st.subheader("Basic Information")
        email = st.text_input("Email", placeholder="your@email.com", key="reg_email")
        password = st.text_input("Password", type="password", placeholder="Minimum 8 characters", key="reg_password")
        password_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm")
        
        st.subheader("Profile Information (Optional)")
        name = st.text_input("Name", placeholder="John Doe", key="reg_name")
        age = st.number_input("Age", min_value=1, max_value=120, value=None, key="reg_age")
        occupation = st.text_input("Occupation", placeholder="Developer", key="reg_occupation")
        
        submit_button = st.form_submit_button("Register", use_container_width=True)
        
        if submit_button:
            if not email or not password:
                st.error("Email and password are required.")
            elif password != password_confirm:
                st.error("Passwords do not match.")
            else:
                try:
                    profile_data = {}
                    if name:
                        profile_data["name"] = name
                    if age:
                        profile_data["age"] = int(age)
                    if occupation:
                        profile_data["occupation"] = occupation
                    
                    from src.utils.async_helpers import run_async
                    from config.database import db
                    
                    # Check if database is available
                    if not db.engine or not db.session_factory:
                        st.error("❌ Database Connection Error")
                        st.info("Database has not been initialized. Please refer to the diagnostic information in the Login tab.")
                        st.stop()
                    
                    user = run_async(user_service.register(email, password, profile_data))
                    st.success("Registration successful! Please login with your credentials.")
                    # Auto-login after registration
                    try:
                        user = run_async(auth_middleware.login(email, password))
                        st.success("Auto-login successful! Redirecting to chat...")
                        st.switch_page("pages/agent_chat.py")
                    except Exception:
                        st.info("Please use the Login tab to sign in.")
                        st.rerun()
                except UserAlreadyExistsError as e:
                    st.error(str(e))
                except ValidationError as e:
                    st.error(str(e))
                except Exception as e:
                    error_msg = str(e)
                    if "Database" in error_msg or "asyncpg" in error_msg or "connection" in error_msg.lower():
                        st.error("❌ Database Connection Error")
                        st.info("Please verify that PostgreSQL is running and refer to the diagnostic information in the Login tab.")
                    else:
                        st.error(f"Registration error: {error_msg}")

