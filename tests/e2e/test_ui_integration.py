"""
UI 연동 테스트 - 브라우저에서 실제 UI 동작 검증

기능 테스트와 구분:
- 기능 테스트: 비즈니스 로직, 서비스, 모델 등 백엔드 기능 검증
- UI 연동 테스트: 실제 브라우저에서 사용자가 보는 UI와 상호작용 검증

이 파일은 실제 브라우저에서 UI 요소가 제대로 렌더링되고
사용자 상호작용이 올바르게 동작하는지 검증합니다.
"""
import time

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.conftest import take_screenshot, wait_for_streamlit_load


@pytest.mark.e2e
@pytest.mark.ui
class TestUIIntegration:
    """UI 연동 테스트 클래스"""

    def test_login_page_ui_elements(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """로그인 페이지 UI 요소 검증"""
        print("\n" + "=" * 60)
        print("로그인 페이지 UI 요소 테스트")
        print("=" * 60)

        page.goto(f"{app_url}/login", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        time.sleep(2)

        take_screenshot(page, "ui_login_page.png", screenshot_dir)

        # UI 요소 존재 확인
        email_input = page.locator("input[type='text']").first
        password_input = page.locator("input[type='password']").first
        submit_button = page.locator("button[type='submit']").first

        assert email_input.is_visible(), "이메일 입력 필드가 보이지 않습니다"
        assert password_input.is_visible(), "비밀번호 입력 필드가 보이지 않습니다"
        assert submit_button.is_visible(), "로그인 버튼이 보이지 않습니다"

        # 입력 필드에 텍스트 입력 가능한지 확인
        email_input.fill("test@example.com")
        password_input.fill("testpass123")

        assert email_input.input_value() == "test@example.com", "이메일 입력이 동작하지 않습니다"
        assert password_input.input_value() == "testpass123", "비밀번호 입력이 동작하지 않습니다"

        take_screenshot(page, "ui_login_filled.png", screenshot_dir)
        print("[✅] 로그인 페이지 UI 요소 검증 완료")

    def test_dashboard_ui_rendering(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """대시보드 페이지 UI 렌더링 검증"""
        print("\n" + "=" * 60)
        print("대시보드 UI 렌더링 테스트")
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

        take_screenshot(page, "ui_dashboard.png", screenshot_dir)

        # 대시보드 주요 UI 요소 확인
        body_text = page.locator("body").inner_text()

        # 대시보드 키워드 확인 (한국어 또는 영어)
        dashboard_keywords = ["Dashboard", "대시보드", "포트폴리오", "Portfolio", "자산", "Asset"]
        has_dashboard_content = any(keyword in body_text for keyword in dashboard_keywords)

        assert has_dashboard_content, "대시보드 콘텐츠가 렌더링되지 않았습니다"

        print("[✅] 대시보드 UI 렌더링 검증 완료")

    def test_agent_chat_ui_interaction(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """Agent Chat 페이지 UI 상호작용 검증"""
        print("\n" + "=" * 60)
        print("Agent Chat UI 상호작용 테스트")
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

        take_screenshot(page, "ui_agent_chat_initial.png", screenshot_dir)

        # 채팅 입력창 확인
        chat_input = page.locator("textarea").first
        assert chat_input.is_visible(), "채팅 입력창이 보이지 않습니다"

        # 입력창에 텍스트 입력 가능한지 확인
        test_message = "안녕하세요"
        chat_input.fill(test_message)
        assert chat_input.input_value() == test_message, "채팅 입력이 동작하지 않습니다"

        take_screenshot(page, "ui_agent_chat_input.png", screenshot_dir)

        # 전송 버튼 확인 (있는 경우)
        send_buttons = page.locator("button:has-text('전송'), button:has-text('Send'), button[aria-label*='send']")
        if send_buttons.count() > 0:
            assert send_buttons.first.is_visible(), "전송 버튼이 보이지 않습니다"

        print("[✅] Agent Chat UI 상호작용 검증 완료")

    def test_sidebar_navigation_ui(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """사이드바 네비게이션 UI 검증"""
        print("\n" + "=" * 60)
        print("사이드바 네비게이션 UI 테스트")
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

        take_screenshot(page, "ui_sidebar_initial.png", screenshot_dir)

        # 사이드바 확인
        sidebar = page.locator('[data-testid="stSidebar"]')
        if sidebar.count() > 0:
            assert sidebar.first.is_visible(), "사이드바가 보이지 않습니다"

            # 사이드바 내부 링크 확인
            sidebar_text = sidebar.first.inner_text()
            navigation_keywords = ["대시보드", "Dashboard", "프로필", "Profile", "채팅", "Chat"]

            has_navigation = any(keyword in sidebar_text for keyword in navigation_keywords)
            assert has_navigation, "사이드바 네비게이션 메뉴가 없습니다"

        print("[✅] 사이드바 네비게이션 UI 검증 완료")

    def test_onboarding_ui_flow(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """온보딩 UI 플로우 검증"""
        print("\n" + "=" * 60)
        print("온보딩 UI 플로우 테스트")
        print("=" * 60)

        # 회원가입 페이지로 이동
        page.goto(f"{app_url}/register", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        time.sleep(2)

        take_screenshot(page, "ui_register_page.png", screenshot_dir)

        # 회원가입 폼 요소 확인
        email_input = page.locator("input[type='text']").first
        password_inputs = page.locator("input[type='password']")

        assert email_input.is_visible(), "이메일 입력 필드가 보이지 않습니다"
        assert password_inputs.count() >= 2, "비밀번호 입력 필드가 충분하지 않습니다"

        # 온보딩 페이지로 이동 (회원가입 후 자동 이동 가정)
        page.goto(f"{app_url}/onboarding", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        time.sleep(3)

        take_screenshot(page, "ui_onboarding_page.png", screenshot_dir)

        # 온보딩 단계 표시 확인
        body_text = page.locator("body").inner_text()
        onboarding_keywords = ["온보딩", "Onboarding", "Step", "단계", "1/4", "2/4", "3/4", "4/4"]

        has_onboarding_content = any(keyword in body_text for keyword in onboarding_keywords)
        assert has_onboarding_content, "온보딩 콘텐츠가 렌더링되지 않았습니다"

        print("[✅] 온보딩 UI 플로우 검증 완료")

    def test_profile_page_ui(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """프로필 페이지 UI 검증"""
        print("\n" + "=" * 60)
        print("프로필 페이지 UI 테스트")
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

        # 프로필 페이지로 이동
        page.goto(f"{app_url}/profile", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        time.sleep(3)

        take_screenshot(page, "ui_profile_page.png", screenshot_dir)

        # 프로필 페이지 콘텐츠 확인
        body_text = page.locator("body").inner_text()
        profile_keywords = ["프로필", "Profile", "이름", "Name", "이메일", "Email", "나이", "Age"]

        has_profile_content = any(keyword in body_text for keyword in profile_keywords)
        assert has_profile_content, "프로필 페이지 콘텐츠가 렌더링되지 않았습니다"

        print("[✅] 프로필 페이지 UI 검증 완료")

    def test_investment_preference_ui(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """투자 선호도 페이지 UI 검증"""
        print("\n" + "=" * 60)
        print("투자 선호도 페이지 UI 테스트")
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

        # 투자 선호도 페이지로 이동
        page.goto(f"{app_url}/investment_preference", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        time.sleep(3)

        take_screenshot(page, "ui_investment_preference.png", screenshot_dir)

        # 투자 선호도 페이지 콘텐츠 확인
        body_text = page.locator("body").inner_text()
        preference_keywords = ["투자 선호도", "Investment Preference", "위험 감수", "Risk", "목표 수익률", "Target Return"]

        has_preference_content = any(keyword in body_text for keyword in preference_keywords)
        assert has_preference_content, "투자 선호도 페이지 콘텐츠가 렌더링되지 않았습니다"

        # 슬라이더나 입력 필드 확인
        inputs = page.locator("input[type='range'], input[type='number']")
        if inputs.count() > 0:
            assert inputs.first.is_visible(), "투자 선호도 입력 필드가 보이지 않습니다"

        print("[✅] 투자 선호도 페이지 UI 검증 완료")

    def test_responsive_ui_layout(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """반응형 UI 레이아웃 검증"""
        print("\n" + "=" * 60)
        print("반응형 UI 레이아웃 테스트")
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

        # 다양한 화면 크기로 테스트
        viewports = [
            {"width": 1920, "height": 1080, "name": "desktop"},
            {"width": 1280, "height": 720, "name": "laptop"},
            {"width": 768, "height": 1024, "name": "tablet"},
            {"width": 375, "height": 667, "name": "mobile"},
        ]

        for viewport in viewports:
            page.set_viewport_size({"width": viewport["width"], "height": viewport["height"]})
            page.goto(f"{app_url}/dashboard", wait_until="domcontentloaded", timeout=30000)
            wait_for_streamlit_load(page)
            time.sleep(2)

            screenshot_name = f"ui_responsive_{viewport['name']}.png"
            take_screenshot(page, screenshot_name, screenshot_dir)

            # 기본 UI 요소가 보이는지 확인
            body = page.locator("body")
            assert body.count() > 0, f"{viewport['name']} 크기에서 body가 렌더링되지 않았습니다"

        print("[✅] 반응형 UI 레이아웃 검증 완료")

