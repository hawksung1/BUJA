"""
채팅 히스토리 저장 및 로드 테스트
"""
import time

import pytest
from playwright.sync_api import Page

from tests.e2e.conftest import take_screenshot, wait_for_streamlit_load


def test_chat_save_and_load(page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
    """채팅 메시지가 저장되고 새로고침 후에도 로드되는지 확인"""

    print("\n" + "="*60)
    print("채팅 저장 및 로드 테스트 시작")
    print("="*60)

    # Step 1: 로그인
    print("\n[Step 1] 로그인 페이지로 이동")
    page.goto(f"{app_url}/login", wait_until="domcontentloaded", timeout=30000)
    wait_for_streamlit_load(page)
    time.sleep(3)
    take_screenshot(page, "01_login_page.png", screenshot_dir)

    # 로그인 시도
    print("[Step 1] 로그인 시도")
    try:
        # 모든 input 필드 찾기
        all_inputs = page.locator("input").all()
        email_input = None
        password_input = None

        for inp in all_inputs:
            if not inp.is_visible():
                continue
            placeholder = inp.get_attribute('placeholder') or ''
            input_type = inp.get_attribute('type') or ''
            aria_label = inp.get_attribute('aria-label') or ''

            # API 키 입력 필드가 아닌 것 찾기
            if 'api' not in placeholder.lower() and 'api' not in aria_label.lower():
                if input_type == 'text' and not email_input:
                    email_input = inp
                elif input_type == 'password' and not password_input:
                    password_input = inp

        if email_input and password_input:
            email_input.fill("admin@example.com")
            password_input.fill("admin123")
            time.sleep(0.5)

            submit_button = page.locator("button[type='submit']").first
            if submit_button.count() > 0:
                submit_button.click()
                time.sleep(5)
                take_screenshot(page, "02_after_login.png", screenshot_dir)
        else:
            print("[WARN] 로그인 필드를 찾을 수 없습니다. 수동 로그인이 필요할 수 있습니다.")
    except Exception as e:
        print(f"[WARN] 자동 로그인 실패: {e}")
        print("[INFO] 수동으로 로그인한 후 테스트를 계속하세요.")

    # Step 2: Agent Chat 페이지로 이동
    print("\n[Step 2] Agent Chat 페이지로 이동")
    page.goto(f"{app_url}/agent_chat", wait_until="domcontentloaded", timeout=30000)
    wait_for_streamlit_load(page)
    time.sleep(3)
    take_screenshot(page, "03_agent_chat_initial.png", screenshot_dir)

    # 초기 메시지 확인
    print("[Step 2] 초기 메시지 확인")
    initial_messages = page.locator('[data-testid="stChatMessage"], .stChatMessage, [class*="chatMessage"]')
    initial_count = initial_messages.count()
    print(f"[INFO] 초기 메시지 수: {initial_count}")

    # Step 3: 메시지 전송
    print("\n[Step 3] 테스트 메시지 전송")
    chat_input = page.locator('textarea').first
    if chat_input.count() == 0:
        # 다른 방법으로 찾기
        chat_input = page.locator('input[type="text"][placeholder*="Ask"], input[type="text"][placeholder*="ask"]').first

    if chat_input.count() == 0:
        take_screenshot(page, "04_chat_input_not_found.png", screenshot_dir)
        pytest.fail("채팅 입력 필드를 찾을 수 없습니다.")

    test_message = "테스트 메시지입니다. 이 메시지가 저장되는지 확인합니다."
    chat_input.fill(test_message)
    chat_input.press("Enter")

    print("[Step 3] 응답 대기 중...")
    time.sleep(10)  # 응답 생성 대기
    take_screenshot(page, "05_after_sending_message.png", screenshot_dir)

    # 메시지가 표시되었는지 확인
    messages_after_send = page.locator('[data-testid="stChatMessage"], .stChatMessage, [class*="chatMessage"]')
    messages_count_after = messages_after_send.count()
    print(f"[INFO] 메시지 전송 후 메시지 수: {messages_count_after}")

    # Step 4: 페이지 새로고침
    print("\n[Step 4] 페이지 새로고침")
    page.reload(wait_until="domcontentloaded")
    wait_for_streamlit_load(page)
    time.sleep(5)  # 메시지 로드 대기
    take_screenshot(page, "06_after_reload.png", screenshot_dir)

    # 새로고침 후 메시지 확인
    print("[Step 4] 새로고침 후 메시지 확인")
    messages_after_reload = page.locator('[data-testid="stChatMessage"], .stChatMessage, [class*="chatMessage"]')
    messages_count_after_reload = messages_after_reload.count()
    print(f"[INFO] 새로고침 후 메시지 수: {messages_count_after_reload}")

    # 페이지 텍스트에서 테스트 메시지 확인
    page_text = page.locator("body").inner_text()
    has_test_message = test_message in page_text or "테스트 메시지" in page_text

    print(f"[INFO] 페이지에 테스트 메시지 포함 여부: {has_test_message}")

    # 검증
    if messages_count_after_reload == 0 and not has_test_message:
        take_screenshot(page, "07_no_messages_after_reload.png", screenshot_dir)
        pytest.fail(f"❌ 새로고침 후 메시지가 로드되지 않았습니다! (메시지 수: {messages_count_after_reload})")
    elif messages_count_after_reload > 0 or has_test_message:
        print("✅ 새로고침 후 메시지가 로드되었습니다!")

    # Step 5: 두 번째 메시지 전송 및 확인
    print("\n[Step 5] 두 번째 메시지 전송")
    time.sleep(2)
    chat_input = page.locator('textarea').first
    if chat_input.count() == 0:
        chat_input = page.locator('input[type="text"][placeholder*="Ask"], input[type="text"][placeholder*="ask"]').first

    if chat_input.count() > 0:
        second_message = "두 번째 테스트 메시지입니다."
        chat_input.fill(second_message)
        chat_input.press("Enter")
        time.sleep(8)
        take_screenshot(page, "08_after_second_message.png", screenshot_dir)

        # 다시 새로고침
        print("[Step 5] 다시 새로고침")
        page.reload(wait_until="domcontentloaded")
        wait_for_streamlit_load(page)
        time.sleep(5)
        take_screenshot(page, "09_after_second_reload.png", screenshot_dir)

        # 두 번째 메시지도 확인
        page_text_2 = page.locator("body").inner_text()
        has_second_message = second_message in page_text_2 or "두 번째" in page_text_2
        print(f"[INFO] 두 번째 메시지 포함 여부: {has_second_message}")

        if has_second_message:
            print("✅ 두 번째 메시지도 저장되었습니다!")
        else:
            print("⚠️ 두 번째 메시지가 저장되지 않았을 수 있습니다.")

    print("\n" + "="*60)
    print("✅ 채팅 저장 및 로드 테스트 완료!")
    print("="*60)
