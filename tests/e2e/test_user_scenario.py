"""
사용자 시나리오 E2E 테스트
USER_SCENARIO.md에 정의된 시나리오를 따라 테스트

주의: 이 테스트는 실제 앱이 실행 중이어야 합니다.
로그인 필드 선택이 복잡하므로, 기존 test_streamlit_login.py의 방식을 참고하세요.
"""
import pytest
import time
from playwright.sync_api import Page, expect
from tests.e2e.conftest import wait_for_streamlit_load, take_screenshot

# 로그인은 기존 테스트를 재사용하거나 수동으로 진행
# 여기서는 Agent Chat 페이지로 직접 이동하는 것으로 가정


def test_complete_user_scenario(page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
    """전체 사용자 시나리오 테스트
    
    참고: 로그인은 수동으로 진행하거나 기존 test_streamlit_login.py 테스트를 먼저 실행하세요.
    여기서는 이미 로그인된 상태를 가정하고 Agent Chat 기능을 테스트합니다.
    """
    from tests.e2e.conftest import wait_for_streamlit_load
    
    print("\n" + "="*60)
    print("사용자 시나리오 테스트 시작")
    print("="*60)
    
    # ============================================================
    # Step 1: 로그인 (기존 테스트 재사용 또는 수동 진행 필요)
    # ============================================================
    print("\n[Step 1] 로그인")
    print("[INFO] 로그인은 별도로 진행하거나 기존 test_streamlit_login.py를 사용하세요.")
    print("[INFO] 여기서는 Agent Chat 페이지로 직접 이동합니다.")
    
    # 로그인 페이지로 이동 (자동 로그인 또는 수동 로그인 가정)
    page.goto(f"{app_url}/login", wait_until="domcontentloaded", timeout=30000)
    wait_for_streamlit_load(page)
    time.sleep(2)
    
    # 간단한 로그인 시도 (기존 테스트 방식)
    try:
        email_inputs = page.locator("input[type='text']")
        password_inputs = page.locator("input[type='password']")
        
        if email_inputs.count() > 0 and password_inputs.count() > 0:
            # 모든 input 중에서 visible하고 API 키가 아닌 것 찾기
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
    
    take_screenshot(page, "01_after_login_attempt.png", screenshot_dir)
    
    # ============================================================
    # Step 2: 온보딩 (이미 완료된 경우 스킵)
    # ============================================================
    current_url = page.url
    if "onboarding" in current_url.lower():
        print("\n[Step 2] 온보딩 프로세스")
        # 온보딩이 필요한 경우
        # 여기서는 간단히 스킵하고 Agent Chat으로 이동
        pass
    else:
        print("\n[Step 2] 온보딩 완료됨 - Agent Chat으로 이동")
    
    # ============================================================
    # Step 3: Agent Chat 페이지로 이동
    # ============================================================
    print("\n[Step 3] Agent Chat 페이지로 이동")
    page.goto(f"{app_url}/agent_chat", wait_until="domcontentloaded", timeout=30000)
    wait_for_streamlit_load(page)
    time.sleep(2)
    take_screenshot(page, "03_agent_chat_page.png", screenshot_dir)
    
    # 채팅 입력 필드 확인
    page.wait_for_selector('textarea', timeout=10000)
    chat_input = page.locator('textarea').first
    assert chat_input.is_visible(), "채팅 입력 필드를 찾을 수 없습니다"
    
    # ============================================================
    # Step 4: 첫 번째 질문 - 한국어로 질문
    # ============================================================
    print("\n[Step 4] 첫 번째 질문 전송 (한국어)")
    first_message = "안녕하세요! 5년 후 주택 구매를 목표로 하고 있습니다. 어떻게 투자 계획을 세워야 할까요?"
    chat_input.fill(first_message)
    chat_input.press("Enter")
    
    print("[Step 4] 응답 대기 중...")
    time.sleep(8)  # 응답 생성 대기
    take_screenshot(page, "04_first_response.png", screenshot_dir)
    
    # 응답 확인
    page.wait_for_selector('[data-testid="stChatMessage"]', timeout=30000)
    assistant_messages = page.locator('[data-testid="stChatMessage"]')
    
    if assistant_messages.count() > 0:
        last_message = assistant_messages.last
        response_text = last_message.text_content()
        
        print(f"[Step 4] 응답 확인: {len(response_text)}자")
        print(f"[Step 4] 응답 내용 (처음 200자): {response_text[:200]}...")
        
        # 한국어로 응답했는지 확인
        has_korean = any(ord(char) > 127 for char in response_text)
        assert has_korean, "응답이 한국어로 작성되지 않았습니다!"
        print("[Step 4] ✅ 한국어 응답 확인")
        
        # 기본 정보를 다시 요청하지 않는지 확인
        should_not_ask = ["위험 감수 성향", "투자 목표", "재무 상황", "risk tolerance", "investment goals", "financial situation"]
        asks_basic_info = any(keyword in response_text for keyword in should_not_ask)
        assert not asks_basic_info, "기본 정보를 다시 요청하고 있습니다!"
        print("[Step 4] ✅ 기본 정보 재요청 없음 확인")
    else:
        pytest.fail("응답이 표시되지 않았습니다")
    
    # ============================================================
    # Step 5: 두 번째 질문 - 포트폴리오 분석 요청
    # ============================================================
    print("\n[Step 5] 두 번째 질문 전송")
    time.sleep(2)
    chat_input = page.locator('textarea').first
    second_message = "현재 포트폴리오를 분석해주세요."
    chat_input.fill(second_message)
    chat_input.press("Enter")
    
    print("[Step 5] 응답 대기 중...")
    time.sleep(8)
    take_screenshot(page, "05_second_response.png", screenshot_dir)
    
    # 응답 확인
    time.sleep(2)
    assistant_messages = page.locator('[data-testid="stChatMessage"]')
    if assistant_messages.count() > 1:
        last_message = assistant_messages.last
        response_text = last_message.text_content()
        print(f"[Step 5] 응답 확인: {len(response_text)}자")
        
        # 한국어 응답 확인
        has_korean = any(ord(char) > 127 for char in response_text)
        assert has_korean, "응답이 한국어로 작성되지 않았습니다!"
        print("[Step 5] ✅ 한국어 응답 확인")
    
    # ============================================================
    # Step 6: 채팅 히스토리 확인 (페이지 새로고침 후)
    # ============================================================
    print("\n[Step 6] 채팅 히스토리 저장 확인")
    page.reload(wait_until="domcontentloaded")
    wait_for_streamlit_load(page)
    time.sleep(3)
    take_screenshot(page, "06_chat_history_loaded.png", screenshot_dir)
    
    # 이전 메시지들이 로드되었는지 확인
    chat_messages = page.locator('[data-testid="stChatMessage"]')
    message_count = chat_messages.count()
    
    print(f"[Step 6] 로드된 메시지 수: {message_count}")
    assert message_count >= 2, f"채팅 히스토리가 저장되지 않았습니다 (메시지 수: {message_count})"
    print("[Step 6] ✅ 채팅 히스토리 저장 확인")
    
    print("\n" + "="*60)
    print("✅ 사용자 시나리오 테스트 완료!")
    print("="*60)

