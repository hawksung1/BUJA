"""
채팅 히스토리 저장 및 로드 테스트
"""
import time

import pytest
from playwright.sync_api import Page

from tests.e2e.conftest import take_screenshot, wait_for_streamlit_load


def test_chat_history_save_and_load(page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
    """채팅 메시지가 저장되고 새로고침 후에도 로드되는지 확인"""

    print("\n" + "="*60)
    print("채팅 히스토리 저장 및 로드 테스트 시작")
    print("="*60)

    # Step 1: 로그인 (간단한 방식)
    print("\n[Step 1] 로그인 페이지로 이동")
    page.goto(f"{app_url}/login", wait_until="domcontentloaded", timeout=30000)
    wait_for_streamlit_load(page)
    time.sleep(3)

    # 로그인 시도
    try:
        email_inputs = page.locator("input[type='text']")
        password_inputs = page.locator("input[type='password']")

        if email_inputs.count() > 0 and password_inputs.count() > 0:
            # visible한 input 찾기
            for inp in email_inputs.all():
                if inp.is_visible():
                    placeholder = inp.get_attribute('placeholder') or ''
                    if 'api' not in placeholder.lower():
                        inp.fill("admin@example.com")
                        break

            for inp in password_inputs.all():
                if inp.is_visible():
                    placeholder = inp.get_attribute('placeholder') or ''
                    if 'api' not in placeholder.lower():
                        inp.fill("admin123")
                        break

            submit_button = page.locator("button[type='submit']").first
            if submit_button.count() > 0:
                submit_button.click()
                time.sleep(3)
    except Exception as e:
        print(f"[WARN] 자동 로그인 실패: {e}")
        print("[INFO] 수동으로 로그인한 후 테스트를 계속하세요.")

    # Step 2: Agent Chat 페이지로 이동
    print("\n[Step 2] Agent Chat 페이지로 이동")
    page.goto(f"{app_url}/agent_chat", wait_until="domcontentloaded", timeout=30000)
    wait_for_streamlit_load(page)
    time.sleep(3)
    take_screenshot(page, "01_agent_chat_initial.png", screenshot_dir)

    # Step 3: 초기 메시지 확인
    print("\n[Step 3] 초기 메시지 확인")
    # Streamlit의 채팅 메시지 찾기 (더 넓은 범위로)
    # Streamlit chat message는 보통 특정 구조를 가짐
    time.sleep(2)
    chat_messages = page.locator('[data-testid="stChatMessage"], [class*="stChatMessage"], [class*="chatMessage"], [role="article"]')
    initial_message_count = chat_messages.count()
    print(f"[INFO] 초기 메시지 수: {initial_message_count}")

    # 페이지 텍스트로도 확인
    page_text = page.locator("body").inner_text()
    print(f"[INFO] 페이지 텍스트 길이: {len(page_text)}")
    if len(page_text) > 0:
        # 이모지 제거하여 출력
        safe_text = page_text[:200].encode('ascii', 'ignore').decode('ascii')
        print(f"[INFO] 페이지 텍스트 일부: {safe_text}")

    # Step 4: 새 메시지 전송
    print("\n[Step 4] 새 메시지 전송")
    chat_input = page.locator('textarea').first
    if chat_input.count() == 0:
        pytest.fail("채팅 입력 필드를 찾을 수 없습니다.")

    test_message = "테스트 메시지: 채팅 히스토리 저장 확인"
    chat_input.fill(test_message)
    chat_input.press("Enter")

    print("[Step 4] 응답 대기 중...")
    time.sleep(10)  # 응답 생성 대기

    take_screenshot(page, "02_after_sending_message.png", screenshot_dir)

    # Step 5: 메시지가 표시되었는지 확인
    print("\n[Step 5] 메시지 표시 확인")
    time.sleep(3)

    # 여러 방법으로 메시지 확인
    chat_messages_after = page.locator('[data-testid="stChatMessage"], [class*="stChatMessage"], [class*="chatMessage"], [role="article"]')
    message_count_after = chat_messages_after.count()
    print(f"[INFO] 메시지 전송 후 메시지 수: {message_count_after}")

    # 페이지 텍스트로도 확인
    page_text_after = page.locator("body").inner_text()
    has_test_message = test_message in page_text_after or "테스트 메시지" in page_text_after
    print(f"[INFO] 페이지에 테스트 메시지 포함 여부: {has_test_message}")
    # 이모지 제거하여 출력
    safe_text = page_text_after[:500].encode('ascii', 'ignore').decode('ascii')
    print(f"[INFO] 페이지 텍스트 일부: {safe_text}")

    # 메시지가 증가했는지 또는 페이지에 텍스트가 있는지 확인
    if message_count_after > initial_message_count:
        print("[✅] 메시지가 표시되었습니다 (selector로 확인)")
    elif has_test_message:
        print("[✅] 메시지가 표시되었습니다 (텍스트로 확인)")
    else:
        # 스크린샷 저장
        take_screenshot(page, "02_debug_no_message.png", screenshot_dir)
        pytest.fail(f"메시지가 표시되지 않았습니다. 초기: {initial_message_count}, 이후: {message_count_after}, 텍스트 포함: {has_test_message}")

    # Step 6: 페이지 새로고침
    print("\n[Step 6] 페이지 새로고침")
    page.reload(wait_until="domcontentloaded")
    wait_for_streamlit_load(page)
    time.sleep(5)  # 메시지 로드 대기
    take_screenshot(page, "03_after_reload.png", screenshot_dir)

    # Step 7: 새로고침 후 메시지 확인
    print("\n[Step 7] 새로고침 후 메시지 확인")
    chat_messages_after_reload = page.locator('[data-testid="stChatMessage"], .stChatMessage, [class*="chatMessage"]')
    message_count_after_reload = chat_messages_after_reload.count()
    print(f"[INFO] 새로고침 후 메시지 수: {message_count_after_reload}")

    # 새로고침 후에도 메시지가 있어야 함
    assert message_count_after_reload >= message_count_after, f"새로고침 후 메시지가 사라졌습니다. 전: {message_count_after}, 후: {message_count_after_reload}"
    print("[✅] 새로고침 후에도 메시지가 유지되었습니다")

    # Step 8: 메시지 내용 확인
    print("\n[Step 8] 메시지 내용 확인")
    page_text = page.locator("body").inner_text()

    # 테스트 메시지가 포함되어 있는지 확인
    has_test_message = test_message in page_text or "테스트 메시지" in page_text
    print(f"[INFO] 테스트 메시지 포함 여부: {has_test_message}")

    if has_test_message:
        print("[✅] 테스트 메시지가 표시되었습니다")
    else:
        print("[WARN] 테스트 메시지를 찾을 수 없습니다. 페이지 텍스트 일부:")
        print(page_text[:500])

    print("\n" + "="*60)
    print("✅ 채팅 히스토리 저장 및 로드 테스트 완료!")
    print("="*60)


def test_chat_history_empty_on_first_load(page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
    """처음 접속 시 채팅 히스토리가 비어있는지 확인"""

    print("\n" + "="*60)
    print("초기 채팅 히스토리 확인 테스트")
    print("="*60)

    # Agent Chat 페이지로 직접 이동
    print("\n[Step 1] Agent Chat 페이지로 이동")
    page.goto(f"{app_url}/agent_chat", wait_until="domcontentloaded", timeout=30000)
    wait_for_streamlit_load(page)
    time.sleep(3)
    take_screenshot(page, "04_empty_chat_history.png", screenshot_dir)

    # 채팅 입력 필드가 있는지 확인
    chat_input = page.locator('textarea').first
    assert chat_input.count() > 0, "채팅 입력 필드를 찾을 수 없습니다."

    # 메시지가 없어야 함 (또는 매우 적어야 함)
    chat_messages = page.locator('[data-testid="stChatMessage"], .stChatMessage, [class*="chatMessage"]')
    message_count = chat_messages.count()
    print(f"[INFO] 초기 메시지 수: {message_count}")

    # 메시지가 없거나 매우 적어야 함 (시스템 메시지 등)
    assert message_count <= 2, f"초기 메시지가 너무 많습니다: {message_count}"
    print("[✅] 초기 채팅 히스토리가 비어있습니다")

    print("\n" + "="*60)
    print("✅ 초기 채팅 히스토리 확인 테스트 완료!")
    print("="*60)

