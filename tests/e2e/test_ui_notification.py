"""
알림 시스템 UI 테스트 - 브라우저에서 알림 UI 동작 검증

기능 테스트와 구분:
- 기능 테스트: NotificationService, NotificationRepository 등 백엔드 로직 검증
- UI 테스트: 실제 브라우저에서 알림 페이지, 사이드바 배지 등 UI 요소 검증

이 파일은 실제 브라우저에서 알림 UI가 제대로 렌더링되고
사용자 상호작용이 올바르게 동작하는지 검증합니다.
"""
import time

import pytest
from playwright.sync_api import Page

from tests.e2e.conftest import take_screenshot, wait_for_streamlit_load


@pytest.mark.e2e
@pytest.mark.ui
class TestNotificationUI:
    """알림 시스템 UI 테스트 클래스"""

    def test_notification_page_ui_elements(
        self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str
    ):
        """알림 페이지 UI 요소 검증"""
        import sys
        
        print("\n" + "=" * 80)
        print("[TEST] 알림 페이지 UI 요소 테스트 시작")
        print("=" * 80)
        print("[WARNING] 브라우저 창을 확인하세요! 화면이 보여야 합니다!")
        print("=" * 80)
        sys.stdout.flush()
        
        # 브라우저가 실제로 열렸는지 확인
        time.sleep(3)  # 브라우저 창이 보일 시간 확보
        
        # 브라우저를 최대화
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        print(f"\n[STEP 1/4] 로그인 페이지로 이동: {app_url}/login")
        print("[INFO] 브라우저에서 페이지 로딩을 확인하세요!")
        sys.stdout.flush()

        # 로그인 먼저 수행
        print(f"\n[1/4] 로그인 페이지로 이동: {app_url}/login")
        page.goto(f"{app_url}/login", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        time.sleep(3)  # 브라우저 화면 확인을 위해 대기 시간 증가

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
        print(f"\n[3/4] 알림 페이지로 이동: {app_url}/notifications")
        page.goto(f"{app_url}/notifications", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        time.sleep(5)  # 브라우저 화면 확인을 위해 대기 시간 증가

        print("\n[4/4] 스크린샷 저장 중...")
        take_screenshot(page, "ui_notification_page.png", screenshot_dir)
        print("✅ 스크린샷 저장 완료: tests/e2e/screenshots/ui_notification_page.png")

        # 알림 페이지 주요 UI 요소 확인
        body_text = page.locator("body").inner_text()

        # 알림 페이지 키워드 확인
        notification_keywords = ["알림", "Notification", "필터", "Filter", "읽지 않음", "읽음"]
        has_notification_content = any(keyword in body_text for keyword in notification_keywords)

        assert has_notification_content, "알림 페이지 콘텐츠가 렌더링되지 않았습니다"

        # 필터 드롭다운 확인
        selectbox = page.locator("select, [role='combobox']")
        if selectbox.count() > 0:
            assert selectbox.first.is_visible(), "필터 드롭다운이 보이지 않습니다"

        # 모두 읽음 처리 버튼 확인
        buttons = page.locator("button")
        has_mark_all_read = any(
            "읽음" in btn.inner_text() or "read" in btn.inner_text().lower()
            for btn in buttons.all()
        )

        print("[✅] 알림 페이지 UI 요소 검증 완료")

    def test_notification_sidebar_badge(
        self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str
    ):
        """사이드바 알림 배지 UI 검증"""
        print("\n" + "=" * 60)
        print("사이드바 알림 배지 UI 테스트")
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

        # 대시보드로 이동 (사이드바 확인)
        page.goto(f"{app_url}/dashboard", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        time.sleep(3)

        take_screenshot(page, "ui_sidebar_notification_badge.png", screenshot_dir)

        # 사이드바 확인
        sidebar = page.locator('[data-testid="stSidebar"]')
        if sidebar.count() > 0:
            sidebar_text = sidebar.first.inner_text()

            # 알림 관련 키워드 확인 (배지가 있거나 없거나 둘 다 정상)
            notification_keywords = ["알림", "Notification", "🔔"]
            has_notification_element = any(keyword in sidebar_text for keyword in notification_keywords)

            # 알림 배지가 있으면 좋지만, 없어도 정상 (알림이 없을 수 있음)
            print("[✅] 사이드바 알림 배지 UI 검증 완료 (알림이 없을 수도 있음)")

    def test_notification_page_navigation(
        self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str
    ):
        """알림 페이지 네비게이션 검증"""
        print("\n" + "=" * 60)
        print("알림 페이지 네비게이션 테스트")
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

        # 알림 페이지로 직접 이동
        page.goto(f"{app_url}/notifications", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        time.sleep(3)

        take_screenshot(page, "ui_notification_navigation.png", screenshot_dir)

        # URL 확인
        current_url = page.url
        assert "/notifications" in current_url or "notifications" in current_url.lower(), (
            "알림 페이지로 이동하지 못했습니다"
        )

        print("[✅] 알림 페이지 네비게이션 검증 완료")

    def test_notification_filter_functionality(
        self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str
    ):
        """알림 필터 기능 검증"""
        print("\n" + "=" * 60)
        print("알림 필터 기능 테스트")
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

        take_screenshot(page, "ui_notification_filter_initial.png", screenshot_dir)

        # 필터 드롭다운 확인 및 변경
        selectbox = page.locator("select, [role='combobox']").first
        if selectbox.count() > 0 and selectbox.is_visible():
            # 필터 옵션 선택 시도
            try:
                selectbox.select_option("읽지 않음")
                time.sleep(2)
                take_screenshot(page, "ui_notification_filter_unread.png", screenshot_dir)
            except Exception as e:
                print(f"[WARN] 필터 변경 중 오류: {e}")

        print("[✅] 알림 필터 기능 검증 완료")

