"""
E2E 테스트 공통 설정 및 Fixtures
"""
import time

import httpx
import pytest
from playwright.sync_api import Browser, Page, sync_playwright

# 테스트 설정
APP_URL = "http://localhost:8501"
TIMEOUT = 30000  # 30초


@pytest.fixture(scope="session")
def browser():
    """Playwright 브라우저 인스턴스 (세션 전체에서 공유)"""
    import sys
    
    print("\n" + "=" * 80)
    print("[BROWSER] 브라우저를 시작합니다...")
    print("=" * 80)
    print("[WARNING] 브라우저 창이 열립니다. 화면을 확인하세요!")
    print("=" * 80)
    sys.stdout.flush()  # 출력 즉시 반영
    
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        headless=False,  # 브라우저가 보이도록 (필수!)
        slow_mo=1500,   # 1.5초씩 천천히 실행 (관찰하기 쉽게)
        args=[
            '--start-maximized',  # 브라우저를 최대화하여 시작
            '--disable-blink-features=AutomationControlled',  # 자동화 감지 비활성화
        ],
    )
    
    print("[OK] 브라우저가 열렸습니다!")
    print("=" * 80)
    sys.stdout.flush()
    
    # 브라우저가 실제로 열릴 때까지 잠시 대기
    time.sleep(2)
    
    yield browser
    
    print("\n" + "=" * 80)
    print("[CLOSE] 브라우저를 닫습니다...")
    print("=" * 80)
    sys.stdout.flush()
    
    browser.close()
    playwright.stop()


@pytest.fixture(scope="function")
def screenshot_dir(tmp_path):
    """스크린샷 저장 디렉토리"""
    import os
    screenshot_path = os.path.join("tests", "e2e", "screenshots")
    os.makedirs(screenshot_path, exist_ok=True)
    return screenshot_path


@pytest.fixture(scope="function")
def page(browser: Browser):
    """각 테스트마다 새로운 페이지 인스턴스"""
    import sys
    
    # 새 페이지 생성
    page = browser.new_page()
    
    # 브라우저 창 크기 설정 (최대화)
    page.set_viewport_size({"width": 1920, "height": 1080})
    
    # 브라우저 창을 앞으로 가져오기 (Windows)
    try:
        # Windows에서 브라우저 창 포커스
        import subprocess
        import platform
        if platform.system() == "Windows":
            # Chrome/Chromium 프로세스 찾아서 포커스
            pass  # Playwright가 자동으로 처리
    except:
        pass
    
    print(f"\n[PAGE] 새 페이지가 열렸습니다: {page.url if page.url else '(아직 URL 없음)'}")
    sys.stdout.flush()
    
    yield page
    
    print(f"[PAGE] 페이지를 닫습니다: {page.url}")
    sys.stdout.flush()
    
    page.close()


@pytest.fixture(scope="function")
def app_url():
    """Streamlit 앱 URL"""
    return APP_URL


@pytest.fixture(scope="function")
def ensure_app_running(app_url: str):
    """Streamlit 앱이 실행 중인지 확인"""
    max_retries = 10
    for i in range(max_retries):
        try:
            response = httpx.get(app_url, timeout=5, follow_redirects=True)
            if response.status_code in [200, 200]:
                print(f"[OK] Streamlit 앱이 {app_url}에서 실행 중입니다 (시도 {i+1}/{max_retries})")
                return True
        except Exception as e:
            if i < max_retries - 1:
                print(f"[INFO] Streamlit 앱 확인 중... (시도 {i+1}/{max_retries}): {str(e)[:50]}")
                time.sleep(2)
            else:
                print(f"[WARN] Streamlit 앱 확인 실패: {str(e)}")

    # 스킵하지 않고 경고만 출력 (테스트는 계속 진행)
    print(f"[WARN] Streamlit 앱이 {app_url}에서 응답하지 않지만 테스트를 계속 진행합니다.")
    return False


@pytest.fixture(scope="function")
def screenshot_dir():
    """스크린샷 저장 디렉토리"""
    import os
    dir_path = "tests/e2e/screenshots"
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


def take_screenshot(page: Page, filename: str, screenshot_dir: str = "tests/e2e/screenshots"):
    """스크린샷 촬영 헬퍼 함수"""
    import os
    os.makedirs(screenshot_dir, exist_ok=True)
    path = f"{screenshot_dir}/{filename}"
    page.screenshot(path=path, full_page=True)
    return path


def wait_for_streamlit_load(page: Page, timeout: int = 10):
    """Streamlit 앱이 완전히 로드될 때까지 대기"""
    # Streamlit 앱의 주요 요소가 로드될 때까지 대기
    try:
        # body가 로드될 때까지 대기
        page.wait_for_selector("body", timeout=timeout * 1000)
        time.sleep(2)  # 추가 렌더링 대기
        return True
    except:
        return False


def navigate_to_page(page: Page, page_name: str, page_title: str = None, wait_time: int = 3):
    """
    Streamlit 페이지로 네비게이션하는 헬퍼 함수
    직접 URL 접근 대신 사이드바 링크를 클릭하여 이동
    
    Args:
        page: Playwright Page 객체
        page_name: 페이지 이름 (예: "dashboard", "profile")
        page_title: 페이지 제목 (예: "대시보드", "프로필") - 링크 찾을 때 사용
        wait_time: 이동 후 대기 시간 (초)
    """
    import time

    # page_title이 없으면 page_name 사용
    if not page_title:
        page_title = page_name

    # 여러 방법으로 링크 찾기
    selectors = [
        f"a[href*='{page_name}']",
        f"button:has-text('{page_title}')",
        f"[data-testid='stPageLink']:has-text('{page_title}')",
        f"a:has-text('{page_title}')",
    ]

    page_link = None
    for selector in selectors:
        try:
            page_link = page.locator(selector).first
            if page_link.count() > 0:
                break
        except:
            continue

    if page_link and page_link.count() > 0:
        try:
            page_link.click()
            wait_for_streamlit_load(page)
            time.sleep(wait_time)
            return True
        except Exception as e:
            print(f"[WARN] {page_title} 링크 클릭 실패: {e}")
            return False
    else:
        print(f"[WARN] {page_title} 링크를 찾을 수 없습니다. 현재 페이지에서 확인합니다.")
        page.wait_for_load_state("networkidle", timeout=10000)
        time.sleep(wait_time)
        return False
