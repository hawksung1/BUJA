"""
Streamlit 메인 페이지 E2E 테스트
"""
import pytest
import time
from playwright.sync_api import Page
from tests.e2e.conftest import take_screenshot, wait_for_streamlit_load


@pytest.mark.e2e
@pytest.mark.playwright
class TestMainPage:
    """메인 페이지 테스트"""
    
    def test_main_page_loads(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """메인 페이지가 정상적으로 로드되는지 확인"""
        page.goto(app_url, wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        
        take_screenshot(page, "01_main_page_loaded.png", screenshot_dir)
        
        # 페이지 제목 확인
        title = page.title()
        assert title is not None, "페이지 제목이 없습니다"
        assert len(title) > 0, "페이지 제목이 비어있습니다"
        
        # 페이지 콘텐츠 확인
        body_text = page.locator("body").inner_text()
        assert len(body_text) > 0, "페이지 콘텐츠가 없습니다"
        assert len(body_text) > 100, "페이지 콘텐츠가 너무 짧습니다"
    
    def test_main_page_has_navigation(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """메인 페이지에 네비게이션 요소가 있는지 확인"""
        page.goto(app_url, wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        
        # 링크 확인
        links = page.locator("a")
        link_count = links.count()
        
        # 버튼 확인
        buttons = page.locator("button")
        button_count = buttons.count()
        
        print(f"[INFO] 링크 수: {link_count}")
        print(f"[INFO] 버튼 수: {button_count}")
        
        # 최소한 하나의 네비게이션 요소가 있어야 함
        assert link_count > 0 or button_count > 0, "네비게이션 요소가 없습니다"
        
        take_screenshot(page, "02_main_page_navigation.png", screenshot_dir)
    
    def test_main_page_to_login_navigation(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """메인 페이지에서 로그인 페이지로 이동"""
        page.goto(app_url, wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        
        # 로그인 링크 찾기
        login_links = page.locator("a").filter(has_text=page.locator("text=/login|로그인/i"))
        if login_links.count() == 0:
            # 버튼으로 찾기
            login_buttons = page.locator("button").filter(has_text=page.locator("text=/login|로그인/i"))
            if login_buttons.count() > 0:
                login_buttons.first.click()
                time.sleep(2)
        else:
            login_links.first.click()
            time.sleep(2)
        
        # 로그인 페이지로 이동했는지 확인
        body_text = page.locator("body").inner_text().lower()
        assert "login" in body_text or "로그인" in body_text, "로그인 페이지로 이동하지 않았습니다"
        
        take_screenshot(page, "03_main_to_login.png", screenshot_dir)
    
    def test_main_page_to_register_navigation(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """메인 페이지에서 회원가입 페이지로 이동"""
        page.goto(app_url, wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        
        # 회원가입 링크 찾기
        register_links = page.locator("a").filter(has_text=page.locator("text=/register|회원가입/i"))
        if register_links.count() == 0:
            # 버튼으로 찾기
            register_buttons = page.locator("button").filter(has_text=page.locator("text=/register|회원가입/i"))
            if register_buttons.count() > 0:
                register_buttons.first.click()
                time.sleep(2)
        else:
            register_links.first.click()
            time.sleep(2)
        
        # 회원가입 페이지로 이동했는지 확인
        body_text = page.locator("body").inner_text().lower()
        assert "register" in body_text or "회원가입" in body_text, "회원가입 페이지로 이동하지 않았습니다"
        
        take_screenshot(page, "04_main_to_register.png", screenshot_dir)

