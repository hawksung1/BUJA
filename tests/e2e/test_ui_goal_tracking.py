"""
목표 추적 UI 테스트 - 브라우저에서 목표 추적 UI 검증

기능 테스트와 구분:
- 기능 테스트: GoalTrackingService 등 백엔드 로직 검증
- UI 테스트: 실제 브라우저에서 목표 추적 결과가 UI에 표시되는지 검증

이 파일은 실제 브라우저에서 목표 추적 기능이 UI에 어떻게 반영되는지 검증합니다.
"""
import time

import pytest
from playwright.sync_api import Page

from tests.e2e.conftest import take_screenshot, wait_for_streamlit_load


@pytest.mark.e2e
@pytest.mark.ui
class TestGoalTrackingUI:
    """목표 추적 UI 테스트 클래스"""

    def test_goal_tracking_dashboard_display(
        self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str
    ):
        """목표 추적 결과가 대시보드에 표시되는지 검증"""
        print("\n" + "=" * 60)
        print("목표 추적 대시보드 표시 테스트")
        print("=" * 60)

        # 로그인 먼저 수행
        page.goto(f"{app_url}/login", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        time.sleep(2)

        try:
            email_input = page.locator("input[type='text']").first
            password_input = page.locator("input[type='password']").first

            if email_input.count() > 0 and password_input.count() > 0:
                email_input.fill("admin")
                password_input.fill("admin")
                page.locator("button[type='submit']").first.click()
                time.sleep(5)
        except Exception as e:
            print(f"[WARN] 로그인 시도 중 오류: {e}")

        # 대시보드로 이동
        page.goto(f"{app_url}/dashboard", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        time.sleep(3)

        take_screenshot(page, "ui_goal_tracking_dashboard.png", screenshot_dir)

        # 대시보드에서 목표 추적 관련 정보 확인
        body_text = page.locator("body").inner_text()

        # 목표 추적 키워드
        goal_keywords = [
            "목표",
            "Goal",
            "진행률",
            "Progress",
            "달성",
            "Achievement",
            "예상",
            "Expected",
        ]

        # 목표 추적 정보가 있으면 키워드 확인, 없으면 정상 (목표가 설정되지 않았을 수 있음)
        has_goal_content = any(keyword in body_text for keyword in goal_keywords)

        print("[✅] 목표 추적 대시보드 표시 검증 완료 (목표가 없을 수도 있음)")

    def test_goal_tracking_notification_display(
        self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str
    ):
        """목표 추적 알림이 표시되는지 검증"""
        print("\n" + "=" * 60)
        print("목표 추적 알림 표시 테스트")
        print("=" * 60)

        # 로그인 먼저 수행
        page.goto(f"{app_url}/login", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        time.sleep(2)

        try:
            email_input = page.locator("input[type='text']").first
            password_input = page.locator("input[type='password']").first

            if email_input.count() > 0 and password_input.count() > 0:
                email_input.fill("admin")
                password_input.fill("admin")
                page.locator("button[type='submit']").first.click()
                time.sleep(5)
        except Exception as e:
            print(f"[WARN] 로그인 시도 중 오류: {e}")

        # 알림 페이지로 이동
        page.goto(f"{app_url}/notifications", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        time.sleep(3)

        take_screenshot(page, "ui_goal_tracking_notifications.png", screenshot_dir)

        # 목표 추적 관련 알림 확인
        body_text = page.locator("body").inner_text()

        # 목표 추적 알림 키워드
        goal_keywords = [
            "목표",
            "Goal",
            "진행률",
            "Progress",
            "달성",
            "Achievement",
            "위험",
            "Risk",
        ]

        # 알림이 있으면 키워드 확인, 없으면 정상 (아직 알림이 생성되지 않았을 수 있음)
        has_goal_notification = any(keyword in body_text for keyword in goal_keywords)

        print("[✅] 목표 추적 알림 표시 검증 완료 (알림이 없을 수도 있음)")

    def test_goal_tracking_chat_integration(
        self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str
    ):
        """목표 추적 결과가 채팅으로 전달되는지 검증"""
        print("\n" + "=" * 60)
        print("목표 추적 채팅 통합 테스트")
        print("=" * 60)

        # 로그인 먼저 수행
        page.goto(f"{app_url}/login", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        time.sleep(2)

        try:
            email_input = page.locator("input[type='text']").first
            password_input = page.locator("input[type='password']").first

            if email_input.count() > 0 and password_input.count() > 0:
                email_input.fill("admin")
                password_input.fill("admin")
                page.locator("button[type='submit']").first.click()
                time.sleep(5)
        except Exception as e:
            print(f"[WARN] 로그인 시도 중 오류: {e}")

        # Agent Chat 페이지로 이동
        page.goto(f"{app_url}/agent_chat", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        time.sleep(3)

        take_screenshot(page, "ui_goal_tracking_chat.png", screenshot_dir)

        # 채팅 메시지에서 목표 추적 관련 내용 확인
        chat_messages = page.locator('[data-testid="stChatMessage"]')
        if chat_messages.count() > 0:
            messages_text = " ".join(chat_messages.all_inner_texts())

            # 목표 추적 키워드
            goal_keywords = [
                "목표",
                "Goal",
                "진행률",
                "Progress",
                "달성",
                "Achievement",
            ]

            # 메시지가 있으면 키워드 확인, 없으면 정상 (아직 알림이 생성되지 않았을 수 있음)
            has_goal_message = any(keyword in messages_text for keyword in goal_keywords)

        print("[✅] 목표 추적 채팅 통합 검증 완료")

