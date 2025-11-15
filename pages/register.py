"""
회원가입 페이지
"""
import streamlit as st
from src.services import UserService
from src.exceptions import UserAlreadyExistsError, ValidationError
from src.utils.async_helpers import run_async

st.set_page_config(
    page_title="회원가입 - BUJA",
    page_icon="📝",
    layout="centered"
)

# 공통 사이드바 렌더링
from src.utils.sidebar import render_sidebar
render_sidebar()

st.title("📝 회원가입")

user_service = UserService()

# 회원가입 폼
with st.form("register_form"):
    st.subheader("기본 정보")
    email = st.text_input("이메일", placeholder="your@email.com")
    password = st.text_input("비밀번호", type="password", placeholder="최소 8자 이상")
    password_confirm = st.text_input("비밀번호 확인", type="password")
    
    st.subheader("프로필 정보 (선택사항)")
    name = st.text_input("이름", placeholder="홍길동")
    age = st.number_input("나이", min_value=1, max_value=120, value=None)
    occupation = st.text_input("직업", placeholder="개발자")
    
    submit_button = st.form_submit_button("회원가입", use_container_width=True)
    
    if submit_button:
        if not email or not password:
            st.error("이메일과 비밀번호는 필수입니다.")
        elif password != password_confirm:
            st.error("비밀번호가 일치하지 않습니다.")
        else:
            try:
                profile_data = {}
                if name:
                    profile_data["name"] = name
                if age:
                    profile_data["age"] = int(age)
                if occupation:
                    profile_data["occupation"] = occupation
                
                user = run_async(user_service.register(email, password, profile_data))
                st.success("회원가입이 완료되었습니다!")
                st.info("로그인 페이지로 이동합니다...")
                st.switch_page("pages/login.py")
            except UserAlreadyExistsError as e:
                st.error(str(e))
            except ValidationError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"회원가입 중 오류가 발생했습니다: {str(e)}")

# 로그인 링크
st.markdown("---")
st.markdown("이미 계정이 있으신가요? [로그인](/login)")

