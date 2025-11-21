"""
Streamlit 대시보드 페이지 E2E 테스트
"""
import time

import pytest
from playwright.sync_api import Page

from tests.e2e.conftest import navigate_to_page, take_screenshot, wait_for_streamlit_load


@pytest.mark.e2e
@pytest.mark.playwright
class TestDashboardPage:
    """대시보드 페이지 테스트"""

    def test_dashboard_page_loads(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """대시보드 페이지가 정상적으로 로드되는지 확인"""
        # 먼저 로그인
        page.goto(app_url, wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        time.sleep(2)

        # 로그인 시도
        email_input = page.locator("input[type='text']").first
        password_input = page.locator("input[type='password']").first
        if email_input.count() > 0 and password_input.count() > 0:
            email_input.fill("admin")
            password_input.fill("admin")
            time.sleep(0.5)
            submit_button = page.locator("button[type='submit']").first
            if submit_button.count() > 0:
                submit_button.click()
                time.sleep(5)

        # 사이드바 링크로 대시보드 이동
        navigate_to_page(page, "dashboard", "대시보드", wait_time=3)

        take_screenshot(page, "01_dashboard_page_loaded.png", screenshot_dir)

        # 페이지 제목 확인
        title = page.title()
        assert title is not None, "페이지 제목이 없습니다"

        # 페이지 콘텐츠 확인
        body_text = page.locator("body").inner_text()
        assert len(body_text) > 0, "페이지 콘텐츠가 없습니다"

    def test_dashboard_interactive_elements(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """대시보드의 인터랙티브 요소 확인"""
        # 먼저 로그인 후 대시보드로 이동
        page.goto(app_url, wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        time.sleep(2)

        # 로그인 시도
        email_input = page.locator("input[type='text']").first
        password_input = page.locator("input[type='password']").first
        if email_input.count() > 0 and password_input.count() > 0:
            email_input.fill("admin")
            password_input.fill("admin")
            time.sleep(0.5)
            submit_button = page.locator("button[type='submit']").first
            if submit_button.count() > 0:
                submit_button.click()
                time.sleep(5)

        navigate_to_page(page, "dashboard", "대시보드", wait_time=3)

        # 버튼 확인
        buttons = page.locator("button")
        button_count = buttons.count()
        print(f"[INFO] 버튼 수: {button_count}")

        # 입력 필드 확인
        inputs = page.locator("input, textarea, select")
        input_count = inputs.count()
        print(f"[INFO] 입력 필드 수: {input_count}")

        # 링크 확인
        links = page.locator("a")
        link_count = links.count()
        print(f"[INFO] 링크 수: {link_count}")

        # 최소한 하나의 인터랙티브 요소가 있어야 함
        assert button_count > 0 or input_count > 0 or link_count > 0, "인터랙티브 요소가 없습니다"

        take_screenshot(page, "02_dashboard_elements.png", screenshot_dir)

    def test_dashboard_button_interaction(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """대시보드 버튼 상호작용 테스트"""
        # 먼저 로그인 후 대시보드로 이동
        page.goto(app_url, wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        time.sleep(2)

        # 로그인 시도
        email_input = page.locator("input[type='text']").first
        password_input = page.locator("input[type='password']").first
        if email_input.count() > 0 and password_input.count() > 0:
            email_input.fill("admin")
            password_input.fill("admin")
            time.sleep(0.5)
            submit_button = page.locator("button[type='submit']").first
            if submit_button.count() > 0:
                submit_button.click()
                time.sleep(5)

        navigate_to_page(page, "dashboard", "대시보드", wait_time=3)

        # 첫 번째 버튼 찾기 및 클릭
        buttons = page.locator("button")
        if buttons.count() > 0:
            first_button = buttons.first
            button_text = first_button.inner_text()
            print(f"[INFO] 클릭할 버튼: {button_text[:50]}")

            # 버튼이 보이는지 확인
            assert first_button.is_visible(), "버튼이 보이지 않습니다"

            # 버튼 클릭
            first_button.click()
            time.sleep(2)  # 응답 대기

            take_screenshot(page, "03_dashboard_button_clicked.png", screenshot_dir)

            # 페이지 변경 또는 응답 확인
            body_text = page.locator("body").inner_text()
            assert len(body_text) > 0, "버튼 클릭 후 응답이 없습니다"
        else:
            pytest.skip("대시보드에 버튼이 없습니다")

    def test_dashboard_navigation(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """대시보드 네비게이션 테스트"""
        # 먼저 로그인 후 대시보드로 이동
        page.goto(app_url, wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        time.sleep(2)

        # 로그인 시도
        email_input = page.locator("input[type='text']").first
        password_input = page.locator("input[type='password']").first
        if email_input.count() > 0 and password_input.count() > 0:
            email_input.fill("admin")
            password_input.fill("admin")
            time.sleep(0.5)
            submit_button = page.locator("button[type='submit']").first
            if submit_button.count() > 0:
                submit_button.click()
                time.sleep(5)

        navigate_to_page(page, "dashboard", "대시보드", wait_time=3)

        # 사이드바 또는 네비게이션 링크 확인
        links = page.locator("a")
        if links.count() > 0:
            # 첫 번째 링크 클릭 시도
            first_link = links.first
            link_href = first_link.get_attribute("href")
            link_text = first_link.inner_text()

            print(f"[INFO] 링크 텍스트: {link_text[:50]}")
            print(f"[INFO] 링크 href: {link_href}")

            if link_href and not link_href.startswith("#"):
                first_link.click()
                time.sleep(2)

                take_screenshot(page, "04_dashboard_navigation.png", screenshot_dir)

        # 페이지가 여전히 로드되어 있는지 확인
        body_text = page.locator("body").inner_text()
        assert len(body_text) > 0, "네비게이션 후 페이지가 로드되지 않았습니다"

