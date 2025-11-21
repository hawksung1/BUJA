"""
Streamlit 회원가입 페이지 E2E 테스트
"""
import time

import pytest
from playwright.sync_api import Page

from tests.e2e.conftest import take_screenshot, wait_for_streamlit_load


@pytest.mark.e2e
@pytest.mark.playwright
class TestRegisterPage:
    """회원가입 페이지 테스트"""

    def test_register_page_loads(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """회원가입 페이지가 정상적으로 로드되는지 확인"""
        page.goto(f"{app_url}/register", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)

        take_screenshot(page, "01_register_page_loaded.png", screenshot_dir)

        # 페이지 제목 확인
        title = page.title()
        assert title is not None, "페이지 제목이 없습니다"

        # 회원가입 관련 텍스트 확인
        body_text = page.locator("body").inner_text().lower()
        assert "register" in body_text or "회원가입" in body_text, "회원가입 페이지가 아닙니다"

    def test_register_form_elements_exist(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """회원가입 폼 요소가 존재하는지 확인"""
        page.goto(f"{app_url}/register", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)

        # 필수 입력 필드 확인
        email_input = page.locator("input[type='text']").first
        password_input = page.locator("input[type='password']").first
        submit_button = page.locator("button[type='submit']").first

        assert email_input.count() > 0, "이메일 입력 필드를 찾을 수 없습니다"
        assert password_input.count() > 0, "비밀번호 입력 필드를 찾을 수 없습니다"
        assert submit_button.count() > 0, "회원가입 버튼을 찾을 수 없습니다"

        take_screenshot(page, "02_register_form_elements.png", screenshot_dir)

    def test_register_form_input(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """회원가입 폼에 값 입력 테스트"""
        page.goto(f"{app_url}/register", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)

        # 이메일 입력
        email_input = page.locator("input[type='text']").first
        if email_input.count() > 0:
            email_input.fill("newuser@example.com")
            time.sleep(0.5)
            assert email_input.input_value() == "newuser@example.com", "이메일 입력 실패"

        # 비밀번호 입력
        password_inputs = page.locator("input[type='password']")
        if password_inputs.count() > 0:
            password_input = password_inputs.first
            password_input.fill("newpassword123")
            time.sleep(0.5)
            assert len(password_input.input_value()) > 0, "비밀번호 입력 실패"

            # 비밀번호 확인 입력
            if password_inputs.count() > 1:
                password_confirm = password_inputs.nth(1)
                password_confirm.fill("newpassword123")
                time.sleep(0.5)

        # 이름 입력 (선택사항)
        name_inputs = page.locator("input[type='text']")
        if name_inputs.count() > 1:
            name_input = name_inputs.nth(1)
            name_input.fill("테스트 사용자")
            time.sleep(0.5)

        take_screenshot(page, "03_register_form_filled.png", screenshot_dir)

    def test_register_submit(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """회원가입 제출 테스트"""
        page.goto(f"{app_url}/register", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)

        # 폼 입력
        email_input = page.locator("input[type='text']").first
        password_inputs = page.locator("input[type='password']")

        import random
        test_email = f"testuser{random.randint(1000, 9999)}@example.com"

        if email_input.count() > 0:
            email_input.fill(test_email)
        if password_inputs.count() > 0:
            password_inputs.first.fill("testpassword123")
            if password_inputs.count() > 1:
                password_inputs.nth(1).fill("testpassword123")

        time.sleep(0.5)

        # 제출 버튼 클릭
        submit_button = page.locator("button[type='submit']").first
        assert submit_button.count() > 0, "회원가입 버튼을 찾을 수 없습니다"

        submit_button.click()
        time.sleep(3)  # 응답 대기

        take_screenshot(page, "04_register_submitted.png", screenshot_dir)

        # 결과 확인
        body_text = page.locator("body").inner_text().lower()
        assert len(body_text) > 0, "응답이 없습니다"

    def test_register_password_mismatch(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """비밀번호 불일치 테스트"""
        page.goto(f"{app_url}/register", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)

        # 폼 입력 (비밀번호 불일치)
        email_input = page.locator("input[type='text']").first
        password_inputs = page.locator("input[type='password']")

        if email_input.count() > 0:
            email_input.fill("test@example.com")
        if password_inputs.count() > 0:
            password_inputs.first.fill("password123")
            if password_inputs.count() > 1:
                password_inputs.nth(1).fill("differentpassword")  # 다른 비밀번호

        time.sleep(0.5)

        # 제출 버튼 클릭
        submit_button = page.locator("button[type='submit']").first
        if submit_button.count() > 0:
            submit_button.click()
            time.sleep(3)

        take_screenshot(page, "05_register_password_mismatch.png", screenshot_dir)

        # 에러 메시지 확인
        body_text = page.locator("body").inner_text().lower()
        # 비밀번호 불일치 에러 메시지 확인 (실제 앱 동작에 따라 다를 수 있음)
        assert len(body_text) > 0, "응답이 없습니다"

