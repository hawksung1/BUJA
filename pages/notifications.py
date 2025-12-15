"""
알림 페이지
"""
import streamlit as st

from src.middleware import auth_middleware
from src.models.notification import NotificationStatus
from src.services.notification_service import NotificationService
from src.utils.async_helpers import run_async

st.set_page_config(
    page_title="알림 - BUJA",
    page_icon="🔔",
    layout="wide"
)

# Authentication check
if not auth_middleware.is_authenticated():
    st.warning("Login required.")
    st.switch_page("pages/login.py")
    st.stop()

user = auth_middleware.get_current_user()

# 공통 사이드바 렌더링
from src.utils.sidebar import render_sidebar

render_sidebar()

# Initialize notification service
notification_service = NotificationService()

st.title("🔔 알림")

# 알림 필터 및 액션
col1, col2 = st.columns([3, 1])
with col1:
    filter_type = st.selectbox(
        "필터",
        ["전체", "읽지 않음", "읽음"],
        key="notification_filter"
    )
with col2:
    if st.button("모두 읽음 처리", use_container_width=True):
        try:
            run_async(notification_service.mark_all_as_read(user.id))
            st.success("모든 알림을 읽음 처리했습니다.")
            st.rerun()
        except Exception as e:
            st.error(f"오류 발생: {str(e)}")

st.markdown("---")

# 알림 목록 조회
try:
    unread_only = filter_type == "읽지 않음"
    notifications = run_async(
        notification_service.get_user_notifications(
            user.id,
            unread_only=unread_only
        )
    )

    if not notifications:
        st.info("알림이 없습니다." if filter_type == "전체" else f"{filter_type} 알림이 없습니다.")
    else:
        for notification in notifications:
            is_unread = notification.status == NotificationStatus.UNREAD
            
            # 알림 카드
            with st.container():
                border_color = "#ff5722" if is_unread else "transparent"
                st.markdown(
                    f"""
                    <div style="
                        border-left: 4px solid {border_color};
                        padding: 1rem;
                        margin-bottom: 0.5rem;
                        background-color: rgba(255, 255, 255, 0.05);
                        border-radius: 0.5rem;
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div style="flex: 1;">
                                <h4 style="margin: 0; color: {'#fff' if is_unread else '#aaa'};">
                                    {notification.title or '알림'}
                                </h4>
                                <p style="margin: 0.5rem 0 0 0; color: #ccc;">
                                    {notification.message}
                                </p>
                                <small style="color: #888;">
                                    {notification.created_at.strftime('%Y-%m-%d %H:%M') if notification.created_at else ''}
                                </small>
                            </div>
                            <div>
                                {'<span style="background: #ff5722; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem;">읽지 않음</span>' if is_unread else ''}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # 액션 버튼
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    if is_unread and st.button("읽음 처리", key=f"read_{notification.id}"):
                        try:
                            run_async(notification_service.mark_as_read(notification.id))
                            st.success("읽음 처리되었습니다.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"오류 발생: {str(e)}")
                
                with col2:
                    if notification.link and st.button("이동", key=f"link_{notification.id}"):
                        st.switch_page(notification.link)
                
                with col3:
                    if st.button("삭제", key=f"delete_{notification.id}"):
                        try:
                            run_async(notification_service.delete_notification(notification.id))
                            st.success("삭제되었습니다.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"오류 발생: {str(e)}")
                
                st.divider()

except Exception as e:
    st.error(f"알림을 불러오는 중 오류가 발생했습니다: {str(e)}")

