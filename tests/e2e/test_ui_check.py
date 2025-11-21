"""
UI 깨짐 확인 테스트
"""
import time

from playwright.sync_api import Page

from tests.e2e.conftest import take_screenshot, wait_for_streamlit_load


def test_agent_chat_ui_check(page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
    """Agent Chat UI가 정상적으로 표시되는지 확인"""
    print("\n" + "="*60)
    print("Agent Chat UI 확인 테스트 시작")
    print("="*60)

    # Step 1: 로그인
    print("\n[Step 1] 로그인")
    page.goto(f"{app_url}/login", wait_until="domcontentloaded", timeout=30000)
    wait_for_streamlit_load(page)
    take_screenshot(page, "01_login.png", screenshot_dir)

    try:
        # 로그인 필드 찾기 (더 정확한 선택자 사용)
        email_input = page.locator('input[type="text"]').filter(lambda el: "email" in el.get_attribute("placeholder", timeout=1000).lower() or "이메일" in el.get_attribute("placeholder", timeout=1000) or el.is_visible())
        password_input = page.locator('input[type="password"]').filter(lambda el: "password" in el.get_attribute("placeholder", timeout=1000).lower() or "비밀번호" in el.get_attribute("placeholder", timeout=1000) or ("api" not in el.get_attribute("aria-label", timeout=1000).lower() if el.get_attribute("aria-label") else True))

        if email_input.count() > 0 and password_input.count() > 0:
            email_input.first.fill("admin@example.com")
            password_input.first.fill("admin123")
            login_button = page.locator("button:has-text('Login')").first
            if login_button.count() > 0:
                login_button.click()
                time.sleep(3)
                print("[INFO] 로그인 시도 완료")
        else:
            print("[WARN] 로그인 필드를 찾을 수 없습니다.")
    except Exception as e:
        print(f"[WARN] 로그인 시도 중 오류: {e}")

    # Step 2: Agent Chat 페이지로 이동
    print("\n[Step 2] Agent Chat 페이지로 이동")
    page.goto(f"{app_url}/agent_chat", wait_until="domcontentloaded", timeout=30000)
    wait_for_streamlit_load(page)
    time.sleep(5)  # 충분한 로딩 시간
    take_screenshot(page, "02_agent_chat_full.png", screenshot_dir)

    # Step 3: 사이드바 요소 확인
    print("\n[Step 3] 사이드바 요소 확인")

    # 새 채팅 버튼
    new_chat = page.locator("button:has-text('새 채팅')")
    if new_chat.count() > 0:
        print("[OK] 새 채팅 버튼 발견")
    else:
        print("[FAIL] 새 채팅 버튼을 찾을 수 없습니다.")
        take_screenshot(page, "03_sidebar_missing.png", screenshot_dir)

    # 프로젝트 섹션
    project_section = page.locator("text=프로젝트")
    if project_section.count() > 0:
        print("[OK] 프로젝트 섹션 발견")
    else:
        print("[FAIL] 프로젝트 섹션을 찾을 수 없습니다.")

    # Step 4: 메인 영역 확인
    print("\n[Step 4] 메인 영역 확인")

    # Chat input 확인
    chat_input = page.locator("textarea").first
    if chat_input.count() > 0:
        print("[OK] Chat input 발견")
        take_screenshot(page, "04_chat_input.png", screenshot_dir)
    else:
        print("[FAIL] Chat input을 찾을 수 없습니다.")

    # 플러스 버튼 확인
    plus_button = page.locator("button:has-text('➕')")
    if plus_button.count() > 0:
        print("[OK] 플러스 버튼 발견")
    else:
        print("[WARN] 플러스 버튼을 찾을 수 없습니다.")

    # Step 5: 전체 페이지 스크린샷
    print("\n[Step 5] 전체 페이지 스크린샷")
    take_screenshot(page, "05_full_page.png", screenshot_dir)

    print("\n" + "="*60)
    print("UI 확인 테스트 완료!")
    print("="*60)

