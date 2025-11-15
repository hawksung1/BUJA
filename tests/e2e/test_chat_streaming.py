"""
채팅 스트리밍 테스트
"""
import pytest
from playwright.sync_api import Page, expect


def test_chat_streaming_response(page: Page, app_url: str, ensure_app_running):
    """채팅 응답이 스트리밍으로 표시되는지 테스트"""
    from tests.e2e.conftest import wait_for_streamlit_load
    
    # 로그인 페이지로 이동
    page.goto(f"{app_url}/login")
    wait_for_streamlit_load(page)
    
    # 로그인 폼 찾기 및 입력
    page.wait_for_selector('input[type="text"]', timeout=10000)
    email_input = page.locator('input[type="text"]').first
    password_input = page.locator('input[type="password"]').first
    
    email_input.fill("admin@example.com")
    password_input.fill("admin123")
    
    # 로그인 버튼 클릭
    login_button = page.locator('button:has-text("Login")')
    login_button.click()
    
    # Agent Chat 페이지로 이동 대기
    page.wait_for_url(f"{app_url}/agent_chat", timeout=15000)
    wait_for_streamlit_load(page)
    
    # 채팅 입력 필드 찾기
    page.wait_for_selector('textarea', timeout=10000)
    chat_input = page.locator('textarea').first
    
    # 테스트 메시지 전송
    test_message = "안녕하세요! 간단한 투자 조언을 받고 싶습니다."
    chat_input.fill(test_message)
    chat_input.press("Enter")
    
    # 응답이 나타날 때까지 대기
    import time
    time.sleep(5)  # 응답 생성 대기
    
    # 응답 컨테이너 찾기 (assistant 메시지)
    # Streamlit의 채팅 메시지는 특정 구조를 가짐
    page.wait_for_selector('[data-testid="stChatMessage"]', timeout=30000)
    
    # 모든 assistant 메시지 찾기
    assistant_messages = page.locator('[data-testid="stChatMessage"]').filter(has_text="assistant")
    
    # 마지막 응답 확인
    if assistant_messages.count() > 0:
        last_message = assistant_messages.last
        response_text = last_message.text_content()
        
        assert response_text is not None, "응답이 표시되지 않았습니다"
        assert len(response_text) > 0, "응답이 비어있습니다"
        assert len(response_text) > 50, f"응답이 너무 짧습니다: {len(response_text)}자"
        
        print(f"✅ 스트리밍 응답 확인: {len(response_text)}자")
        print(f"응답 내용 (처음 200자): {response_text[:200]}...")
    else:
        # 스크린샷으로 디버깅
        page.screenshot(path="tests/e2e/screenshots/chat_streaming_debug.png", full_page=True)
        pytest.fail("Assistant 메시지를 찾을 수 없습니다. 스크린샷을 확인하세요.")

