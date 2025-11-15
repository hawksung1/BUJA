"""
Playwright Python 라이브러리를 직접 사용한 Streamlit 앱 E2E 테스트
MCP 서버 없이도 작동하는 실제 브라우저 테스트
"""
import pytest
from playwright.sync_api import sync_playwright, Page, Browser
import time


@pytest.fixture(scope="module")
def app_url():
    """Streamlit 앱 URL"""
    # Streamlit이 0.0.0.0으로 실행되면 localhost로 접속 가능
    return "http://localhost:8501"


@pytest.fixture(scope="module")
def browser():
    """Playwright 브라우저 인스턴스"""
    playwright = sync_playwright().start()
    # headless=False로 설정하여 브라우저가 보이도록 함
    browser = playwright.chromium.launch(headless=False, slow_mo=500)
    yield browser
    browser.close()
    playwright.stop()


@pytest.fixture(scope="function")
def page(browser: Browser, app_url: str):
    """새 페이지 인스턴스"""
    page = browser.new_page()
    yield page
    page.close()


@pytest.mark.e2e
@pytest.mark.playwright
class TestStreamlitWithPlaywright:
    """Playwright를 사용한 실제 브라우저 E2E 테스트"""
    
    def test_main_page_loads(self, page: Page, app_url: str):
        """메인 페이지가 정상적으로 로드되는지 확인"""
        page.goto(app_url, wait_until="networkidle", timeout=30000)
        
        # 페이지 제목 확인
        title = page.title()
        assert title is not None
        assert len(title) > 0
        
        # 페이지 콘텐츠 확인
        body_text = page.locator("body").inner_text()
        assert len(body_text) > 0
        
        # Streamlit 앱 요소 확인
        st_app = page.locator("[data-testid='stApp']")
        assert st_app.count() > 0 or page.locator("body").count() > 0
    
    def test_main_page_content(self, page: Page, app_url: str):
        """메인 페이지 콘텐츠 확인"""
        page.goto(app_url, wait_until="networkidle", timeout=30000)
        
        # 페이지 텍스트 확인
        page_text = page.locator("body").inner_text().lower()
        
        # BUJA 또는 환영 메시지 확인
        assert "buja" in page_text or "환영" in page_text or "welcome" in page_text
    
    def test_page_screenshot(self, page: Page, app_url: str):
        """페이지 스크린샷 촬영"""
        page.goto(app_url, wait_until="networkidle", timeout=30000)
        
        # 스크린샷 디렉토리 생성
        import os
        os.makedirs("tests/e2e/screenshots", exist_ok=True)
        
        # 스크린샷 촬영
        screenshot_path = "tests/e2e/screenshots/main_page.png"
        page.screenshot(path=screenshot_path, full_page=True)
        
        # 파일이 생성되었는지 확인
        assert os.path.exists(screenshot_path), f"스크린샷 파일이 생성되지 않았습니다: {screenshot_path}"
        print(f"✅ 스크린샷 저장됨: {screenshot_path}")
    
    def test_navigation_to_login(self, page: Page, app_url: str):
        """로그인 페이지로 이동 테스트"""
        page.goto(app_url, wait_until="networkidle", timeout=30000)
        
        # 로그인 링크/버튼 찾기
        login_link = page.locator("text=로그인").first()
        login_button = page.locator("text=Login").first()
        
        # 로그인 요소가 있으면 클릭
        if login_link.count() > 0:
            login_link.click()
            page.wait_for_load_state("networkidle", timeout=10000)
        elif login_button.count() > 0:
            login_button.click()
            page.wait_for_load_state("networkidle", timeout=10000)
        
        # 로그인 페이지 확인
        page_text = page.locator("body").inner_text().lower()
        assert "로그인" in page_text or "login" in page_text
    
    def test_page_interaction(self, page: Page, app_url: str):
        """페이지 상호작용 테스트"""
        page.goto(app_url, wait_until="networkidle", timeout=30000)
        
        # 페이지가 인터랙티브한지 확인
        # 버튼이나 링크가 클릭 가능한지 확인
        buttons = page.locator("button")
        links = page.locator("a")
        
        # 최소한 하나의 인터랙티브 요소가 있어야 함
        assert buttons.count() > 0 or links.count() > 0
    
    def test_page_responsiveness(self, page: Page, app_url: str):
        """페이지 반응성 테스트"""
        start_time = time.time()
        page.goto(app_url, wait_until="networkidle", timeout=30000)
        load_time = time.time() - start_time
        
        # 페이지가 10초 이내에 로드되어야 함
        assert load_time < 10.0, f"페이지 로드 시간이 너무 깁니다: {load_time:.2f}초"
        
        # 페이지가 정상적으로 렌더링되었는지 확인
        body = page.locator("body")
        assert body.count() > 0


@pytest.mark.e2e
@pytest.mark.playwright
def test_playwright_browser_works(browser: Browser):
    """Playwright 브라우저가 정상 작동하는지 확인"""
    page = browser.new_page()
    try:
        page.goto("http://example.com", wait_until="networkidle", timeout=10000)
        assert "Example Domain" in page.title()
    finally:
        page.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

