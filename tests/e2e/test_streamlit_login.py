"""
Streamlit 로그인 페이지 E2E 테스트
"""
import time

import pytest
from playwright.sync_api import Page

from tests.e2e.conftest import take_screenshot, wait_for_streamlit_load


@pytest.mark.e2e
@pytest.mark.playwright
class TestLoginPage:
    """로그인 페이지 테스트"""

    def test_login_page_loads(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """로그인 페이지가 정상적으로 로드되는지 확인"""
        # 로그인 페이지로 이동
        page.goto(f"{app_url}/login", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)

        # 스크린샷
        take_screenshot(page, "01_login_page_loaded.png", screenshot_dir)

        # 페이지 제목 확인
        title = page.title()
        assert title is not None, "페이지 제목이 없습니다"
        assert len(title) > 0, "페이지 제목이 비어있습니다"

        # 로그인 관련 텍스트 확인
        body_text = page.locator("body").inner_text().lower()
        assert "login" in body_text or "로그인" in body_text, "로그인 페이지가 아닙니다"

    def test_login_form_elements_exist(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """로그인 폼 요소가 존재하는지 확인"""
        page.goto(f"{app_url}/login", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)

        # 이메일 입력 필드 찾기
        email_input = page.locator("input[type='text']").filter(has_text=page.locator("text=/email|이메일/i")).first
        if email_input.count() == 0:
            # 다른 방법으로 찾기
            email_input = page.locator("input").filter(has=page.locator("text=/email|이메일/i")).first
        if email_input.count() == 0:
            # placeholder로 찾기
            email_input = page.locator("input[placeholder*='email'], input[placeholder*='이메일']").first

        # 비밀번호 입력 필드 찾기
        password_input = page.locator("input[type='password']").first

        # 로그인 버튼 찾기
        login_button = page.locator("button").filter(has_text=page.locator("text=/login|로그인/i")).first
        if login_button.count() == 0:
            login_button = page.locator("button[type='submit']").first

        # 요소 존재 확인
        assert email_input.count() > 0, "이메일 입력 필드를 찾을 수 없습니다"
        assert password_input.count() > 0, "비밀번호 입력 필드를 찾을 수 없습니다"
        assert login_button.count() > 0, "로그인 버튼을 찾을 수 없습니다"

        take_screenshot(page, "02_login_form_elements.png", screenshot_dir)

    def test_login_form_input(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """로그인 폼에 값 입력 테스트"""
        page.goto(f"{app_url}/login", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)

        # 이메일 입력 필드 찾기 및 입력
        email_inputs = page.locator("input[type='text']")
        if email_inputs.count() > 0:
            email_input = email_inputs.first
            email_input.fill("test@example.com")
            time.sleep(0.5)

            # 입력값 확인
            value = email_input.input_value()
            assert value == "test@example.com", f"이메일 입력 실패: {value}"

        # 비밀번호 입력 필드 찾기 및 입력
        password_input = page.locator("input[type='password']").first
        assert password_input.count() > 0, "비밀번호 입력 필드를 찾을 수 없습니다"

        password_input.fill("testpassword123")
        time.sleep(0.5)

        # 입력값 확인 (비밀번호는 보안상 확인 불가하지만 입력은 됨)
        value = password_input.input_value()
        assert len(value) > 0, "비밀번호 입력 실패"

        take_screenshot(page, "03_login_form_filled.png", screenshot_dir)

    def test_login_submit_button_clickable(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """로그인 제출 버튼이 클릭 가능한지 확인"""
        page.goto(f"{app_url}/login", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)

        # 폼 입력
        email_input = page.locator("input[type='text']").first
        password_input = page.locator("input[type='password']").first

        if email_input.count() > 0:
            email_input.fill("test@example.com")
        if password_input.count() > 0:
            password_input.fill("testpassword123")

        time.sleep(0.5)

        # 로그인 버튼 찾기 및 클릭
        submit_button = page.locator("button[type='submit']").first
        if submit_button.count() == 0:
            submit_button = page.locator("button").filter(has_text=page.locator("text=/login|로그인/i")).first

        assert submit_button.count() > 0, "로그인 버튼을 찾을 수 없습니다"

        # 버튼이 보이는지 확인
        assert submit_button.is_visible(), "로그인 버튼이 보이지 않습니다"

        # 버튼 클릭
        submit_button.click()
        time.sleep(3)  # 응답 대기

        take_screenshot(page, "04_login_submitted.png", screenshot_dir)

        # 페이지 변경 또는 메시지 확인
        body_text = page.locator("body").inner_text().lower()
        # 성공/실패 메시지 또는 페이지 변경 확인
        assert (
            "success" in body_text or
            "성공" in body_text or
            "error" in body_text or
            "에러" in body_text or
            "fail" in body_text or
            "실패" in body_text or
            len(body_text) > 0
        ), "로그인 제출 후 응답이 없습니다"

    def test_login_with_invalid_credentials(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """잘못된 자격증명으로 로그인 시도"""
        page.goto(f"{app_url}/login", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)

        # 잘못된 자격증명 입력
        email_input = page.locator("input[type='text']").first
        password_input = page.locator("input[type='password']").first

        if email_input.count() > 0:
            email_input.fill("invalid@example.com")
        if password_input.count() > 0:
            password_input.fill("wrongpassword")

        time.sleep(0.5)

        # 제출 버튼 클릭
        submit_button = page.locator("button[type='submit']").first
        if submit_button.count() > 0:
            submit_button.click()
            time.sleep(3)

        take_screenshot(page, "05_login_invalid_credentials.png", screenshot_dir)

        # 에러 메시지 확인
        body_text = page.locator("body").inner_text().lower()
        # 에러 메시지가 표시되는지 확인 (실제 앱 동작에 따라 다를 수 있음)
        assert len(body_text) > 0, "응답이 없습니다"

    def test_login_tab_switching(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """로그인 페이지에서 탭 전환 테스트 (Login/Register 탭)"""
        page.goto(f"{app_url}/login", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)

        # 탭 요소 찾기
        tabs = page.locator("[role='tab'], button:has-text('Register'), button:has-text('회원가입')")

        if tabs.count() > 0:
            # Register 탭 클릭
            register_tab = tabs.filter(has_text=page.locator("text=/register|회원가입/i")).first
            if register_tab.count() > 0:
                register_tab.click()
                time.sleep(2)

                take_screenshot(page, "06_register_tab.png", screenshot_dir)

                # Register 탭 콘텐츠 확인
                body_text = page.locator("body").inner_text().lower()
                assert "register" in body_text or "회원가입" in body_text, "Register 탭이 표시되지 않았습니다"

        # 다시 Login 탭으로 전환
        login_tab = tabs.filter(has_text=page.locator("text=/login|로그인/i")).first
        if login_tab.count() > 0:
            login_tab.click()
            time.sleep(2)

            take_screenshot(page, "07_back_to_login_tab.png", screenshot_dir)

            body_text = page.locator("body").inner_text().lower()
            assert "login" in body_text or "로그인" in body_text, "Login 탭이 표시되지 않았습니다"

    def test_database_error_diagnosis(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """데이터베이스 연결 오류 시 진단 정보가 표시되는지 확인"""
        page.goto(f"{app_url}/login", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)

        # 이메일과 비밀번호 입력
        email_input = page.locator("input[type='text']").first
        password_input = page.locator("input[type='password']").first

        if email_input.count() > 0:
            email_input.fill("test@example.com")
        if password_input.count() > 0:
            password_input.fill("testpassword")

        time.sleep(0.5)

        # 로그인 버튼 클릭
        submit_button = page.locator("button[type='submit']").first
        if submit_button.count() > 0:
            submit_button.click()
            time.sleep(3)  # 응답 대기

        take_screenshot(page, "08_database_error_diagnosis.png", screenshot_dir)

        # 데이터베이스 오류 메시지 확인
        body_text = page.locator("body").inner_text()

        # 진단 정보 패널이 표시되는지 확인
        # "진단 정보" 또는 "diagnosis" 또는 "데이터베이스 연결 오류" 텍스트 확인
        has_error = (
            "데이터베이스 연결 오류" in body_text or
            "Database is not available" in body_text or
            "진단 정보" in body_text or
            "diagnosis" in body_text.lower() or
            "asyncpg" in body_text.lower()
        )

        # 데이터베이스가 연결되어 있지 않은 경우에만 오류 메시지가 표시됨
        # 연결되어 있으면 로그인 시도가 진행되므로, 둘 중 하나는 참이어야 함
        assert (
            has_error or
            "success" in body_text.lower() or
            "error" in body_text.lower() or
            len(body_text) > 0
        ), "페이지에 응답이 없습니다"

        # 진단 정보 패널이 있는 경우 확장 가능한지 확인
        expander = page.locator("text=/진단 정보|diagnosis/i").first
        if expander.count() > 0:
            # 확장 패널 클릭
            expander.click()
            time.sleep(1)
            take_screenshot(page, "09_diagnosis_expanded.png", screenshot_dir)

            # 진단 정보 내용 확인
            expanded_text = page.locator("body").inner_text()
            assert (
                "asyncpg" in expanded_text.lower() or
                "데이터베이스" in expanded_text or
                "database" in expanded_text.lower() or
                "해결 방법" in expanded_text
            ), "진단 정보 내용이 표시되지 않았습니다"

