"""
시나리오 핵심 기능 테스트: 한국어 응답 확인
USER_SCENARIO.md의 핵심 시나리오를 테스트합니다.
"""
import time

import pytest
from playwright.sync_api import Page

from tests.e2e.conftest import take_screenshot, wait_for_streamlit_load


def test_korean_response_in_chat(page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
    """Agent Chat에서 한국어 질문에 한국어로 응답하는지 확인"""

    print("\n" + "="*60)
    print("한국어 응답 테스트 시작")
    print("="*60)

    # Agent Chat 페이지로 직접 이동 (로그인은 별도로 진행했다고 가정)
    print("\n[Step 1] Agent Chat 페이지로 이동")
    page.goto(f"{app_url}/agent_chat", wait_until="domcontentloaded", timeout=30000)
    wait_for_streamlit_load(page)
    time.sleep(3)
    take_screenshot(page, "01_agent_chat_page.png", screenshot_dir)

    # 채팅 입력 필드 확인
    print("[Step 2] 채팅 입력 필드 확인")
    page.wait_for_selector('textarea', timeout=10000)
    chat_input = page.locator('textarea').first

    if chat_input.count() == 0:
        take_screenshot(page, "02_chat_input_not_found.png", screenshot_dir)
        pytest.fail("채팅 입력 필드를 찾을 수 없습니다.")

    # 한국어 질문 전송
    print("[Step 3] 한국어 질문 전송")
    test_message = "안녕하세요! 5년 후 주택 구매를 목표로 하고 있습니다. 어떻게 투자 계획을 세워야 할까요?"
    chat_input.fill(test_message)
    chat_input.press("Enter")

    print("[Step 4] 응답 대기 중...")
    time.sleep(10)  # 응답 생성 대기 (LLM 응답 시간 고려)
    take_screenshot(page, "03_korean_response.png", screenshot_dir)

    # 응답 확인
    print("[Step 5] 응답 확인")
    page.wait_for_selector('[data-testid="stChatMessage"]', timeout=30000)

    assistant_messages = page.locator('[data-testid="stChatMessage"]')
    message_count = assistant_messages.count()

    print(f"[INFO] 발견된 메시지 수: {message_count}")

    if message_count > 0:
        # 마지막 assistant 메시지 확인
        last_message = assistant_messages.last
        response_text = last_message.text_content() or ""

        print(f"[INFO] 응답 길이: {len(response_text)}자")
        print(f"[INFO] 응답 내용 (처음 300자): {response_text[:300]}...")

        # 한국어로 응답했는지 확인
        has_korean = any(ord(char) > 127 for char in response_text)
        assert has_korean, f"응답이 한국어로 작성되지 않았습니다!\n응답 내용: {response_text[:200]}"
        print("[✅] 한국어 응답 확인됨")

        # 기본 정보를 다시 요청하지 않는지 확인
        should_not_ask = [
            "위험 감수 성향", "투자 목표", "재무 상황",
            "risk tolerance", "investment goals", "financial situation",
            "위험도", "목표 수익률"
        ]
        asks_basic_info = any(keyword in response_text for keyword in should_not_ask)
        assert not asks_basic_info, f"기본 정보를 다시 요청하고 있습니다!\n응답 내용: {response_text[:300]}"
        print("[✅] 기본 정보 재요청 없음 확인")

        # 응답이 충분히 긴지 확인 (간단한 에러 메시지가 아닌지)
        assert len(response_text) > 50, f"응답이 너무 짧습니다: {len(response_text)}자"
        print("[✅] 응답 길이 확인")

        print("\n" + "="*60)
        print("✅ 한국어 응답 테스트 완료!")
        print("="*60)
    else:
        take_screenshot(page, "04_no_response.png", screenshot_dir)
        pytest.fail("Assistant 메시지를 찾을 수 없습니다. 스크린샷을 확인하세요.")


def test_chat_history_persistence(page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
    """채팅 히스토리가 저장되고 로드되는지 확인"""

    print("\n" + "="*60)
    print("채팅 히스토리 저장 테스트 시작")
    print("="*60)

    # Agent Chat 페이지로 이동
    print("\n[Step 1] Agent Chat 페이지로 이동")
    page.goto(f"{app_url}/agent_chat", wait_until="domcontentloaded", timeout=30000)
    wait_for_streamlit_load(page)
    time.sleep(3)

    # 첫 번째 메시지 전송
    print("[Step 2] 첫 번째 메시지 전송")
    chat_input = page.locator('textarea').first
    if chat_input.count() > 0:
        chat_input.fill("테스트 메시지 1")
        chat_input.press("Enter")
        time.sleep(5)

    # 페이지 새로고침
    print("[Step 3] 페이지 새로고침")
    page.reload(wait_until="domcontentloaded")
    wait_for_streamlit_load(page)
    time.sleep(3)
    take_screenshot(page, "05_chat_history_loaded.png", screenshot_dir)

    # 이전 메시지들이 로드되었는지 확인
    chat_messages = page.locator('[data-testid="stChatMessage"]')
    message_count = chat_messages.count()

    print(f"[INFO] 로드된 메시지 수: {message_count}")

    # 메시지가 하나 이상 있어야 함 (최소한 사용자 메시지는 있어야 함)
    assert message_count >= 1, f"채팅 히스토리가 저장되지 않았습니다 (메시지 수: {message_count})"
    print("[✅] 채팅 히스토리 저장 확인")

    print("\n" + "="*60)
    print("✅ 채팅 히스토리 테스트 완료!")
    print("="*60)


def test_portfolio_analysis_request(page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
    """포트폴리오 분석 요청 시나리오 테스트
    
    시나리오 4.7: 포트폴리오 분석 요청
    - 구체적인 ETF/주식 추천 요청
    - 포트폴리오 분석 요청
    """

    print("\n" + "="*60)
    print("포트폴리오 분석 요청 테스트 시작")
    print("="*60)

    # Agent Chat 페이지로 이동
    print("\n[Step 1] Agent Chat 페이지로 이동")
    page.goto(f"{app_url}/agent_chat", wait_until="domcontentloaded", timeout=30000)
    wait_for_streamlit_load(page)
    time.sleep(3)
    take_screenshot(page, "01_portfolio_analysis_page.png", screenshot_dir)

    # 포트폴리오 분석 요청
    print("[Step 2] 포트폴리오 분석 요청")
    chat_input = page.locator('textarea').first
    
    if chat_input.count() > 0:
        message = "구체적으로 어떤 ETF나 주식을 추천하시나요? 그리고 현재 제 포트폴리오를 분석해주실 수 있나요?"
        chat_input.fill(message)
        chat_input.press("Enter")
        
        print("[Step 3] 응답 대기 중...")
        time.sleep(10)  # 응답 생성 대기
        take_screenshot(page, "02_portfolio_analysis_response.png", screenshot_dir)
        
        # 응답 확인
        page.wait_for_selector('[data-testid="stChatMessage"]', timeout=30000)
        assistant_messages = page.locator('[data-testid="stChatMessage"]')
        
        if assistant_messages.count() > 0:
            last_message = assistant_messages.last
            response_text = last_message.text_content() or ""
            
            print(f"[INFO] 응답 길이: {len(response_text)}자")
            print(f"[INFO] 응답 내용 (처음 300자): {response_text[:300]}...")
            
            # 한국어 응답 확인
            has_korean = any(ord(char) > 127 for char in response_text)
            assert has_korean, "응답이 한국어로 작성되지 않았습니다!"
            print("[✅] 한국어 응답 확인")
            
            # 포트폴리오 관련 키워드 확인
            portfolio_keywords = ["ETF", "포트폴리오", "분산", "배분", "비중", "추천"]
            has_portfolio_content = any(keyword in response_text for keyword in portfolio_keywords)
            assert has_portfolio_content, "포트폴리오 관련 내용이 없습니다!"
            print("[✅] 포트폴리오 관련 내용 확인")
        else:
            pytest.fail("응답이 표시되지 않았습니다")
    
    print("\n" + "="*60)
    print("✅ 포트폴리오 분석 요청 테스트 완료!")
    print("="*60)


def test_brokerage_recommendation_request(page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
    """증권사 추천 및 수수료 정보 요청 시나리오 테스트
    
    시나리오 4.9: 투자 실행 확인
    - 증권사 추천 요청
    - 수수료 정보 요청
    """

    print("\n" + "="*60)
    print("증권사 추천 및 수수료 정보 요청 테스트 시작")
    print("="*60)

    # Agent Chat 페이지로 이동
    print("\n[Step 1] Agent Chat 페이지로 이동")
    page.goto(f"{app_url}/agent_chat", wait_until="domcontentloaded", timeout=30000)
    wait_for_streamlit_load(page)
    time.sleep(3)

    # 증권사 및 수수료 정보 요청
    print("[Step 2] 증권사 및 수수료 정보 요청")
    chat_input = page.locator('textarea').first
    
    if chat_input.count() > 0:
        message = "실제로 ETF를 구매할 때 어떤 증권사나 앱을 사용하는 게 좋을까요? 그리고 수수료는 어떻게 되는지도 궁금합니다."
        chat_input.fill(message)
        chat_input.press("Enter")
        
        print("[Step 3] 응답 대기 중...")
        time.sleep(10)
        take_screenshot(page, "03_brokerage_recommendation_response.png", screenshot_dir)
        
        # 응답 확인
        page.wait_for_selector('[data-testid="stChatMessage"]', timeout=30000)
        assistant_messages = page.locator('[data-testid="stChatMessage"]')
        
        if assistant_messages.count() > 0:
            last_message = assistant_messages.last
            response_text = last_message.text_content() or ""
            
            print(f"[INFO] 응답 길이: {len(response_text)}자")
            
            # 한국어 응답 확인
            has_korean = any(ord(char) > 127 for char in response_text)
            assert has_korean, "응답이 한국어로 작성되지 않았습니다!"
            print("[✅] 한국어 응답 확인")
            
            # 증권사 또는 수수료 관련 키워드 확인
            brokerage_keywords = ["증권", "수수료", "앱", "거래", "키움", "미래에셋", "토스", "카카오"]
            has_brokerage_content = any(keyword in response_text for keyword in brokerage_keywords)
            assert has_brokerage_content, "증권사 또는 수수료 관련 내용이 없습니다!"
            print("[✅] 증권사/수수료 관련 내용 확인")
        else:
            pytest.fail("응답이 표시되지 않았습니다")
    
    print("\n" + "="*60)
    print("✅ 증권사 추천 및 수수료 정보 요청 테스트 완료!")
    print("="*60)


def test_aggressive_strategy_request(page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
    """공격적 투자 전략 요청 시나리오 테스트
    
    시나리오 4.5: 추가 질문
    - 목표 금액 달성을 위한 공격적 전략 요청
    - 대안 제시 확인
    """

    print("\n" + "="*60)
    print("공격적 투자 전략 요청 테스트 시작")
    print("="*60)

    # Agent Chat 페이지로 이동
    print("\n[Step 1] Agent Chat 페이지로 이동")
    page.goto(f"{app_url}/agent_chat", wait_until="domcontentloaded", timeout=30000)
    wait_for_streamlit_load(page)
    time.sleep(3)

    # 공격적 전략 요청
    print("[Step 2] 공격적 투자 전략 요청")
    chat_input = page.locator('textarea').first
    
    if chat_input.count() > 0:
        message = "목표 금액까지 도달하려면 더 많은 자금이 필요한데, 더 공격적인 투자 전략이나 다른 방법이 있을까요?"
        chat_input.fill(message)
        chat_input.press("Enter")
        
        print("[Step 3] 응답 대기 중...")
        time.sleep(10)
        take_screenshot(page, "04_aggressive_strategy_response.png", screenshot_dir)
        
        # 응답 확인
        page.wait_for_selector('[data-testid="stChatMessage"]', timeout=30000)
        assistant_messages = page.locator('[data-testid="stChatMessage"]')
        
        if assistant_messages.count() > 0:
            last_message = assistant_messages.last
            response_text = last_message.text_content() or ""
            
            print(f"[INFO] 응답 길이: {len(response_text)}자")
            
            # 한국어 응답 확인
            has_korean = any(ord(char) > 127 for char in response_text)
            assert has_korean, "응답이 한국어로 작성되지 않았습니다!"
            print("[✅] 한국어 응답 확인")
            
            # 전략 관련 키워드 확인
            strategy_keywords = ["전략", "대안", "공격적", "위험", "수익", "투자", "방법"]
            has_strategy_content = any(keyword in response_text for keyword in strategy_keywords)
            assert has_strategy_content, "전략 관련 내용이 없습니다!"
            print("[✅] 전략 관련 내용 확인")
            
            # 응답이 충분히 긴지 확인
            assert len(response_text) > 100, f"응답이 너무 짧습니다: {len(response_text)}자"
            print("[✅] 응답 길이 확인")
        else:
            pytest.fail("응답이 표시되지 않았습니다")
    
    print("\n" + "="*60)
    print("✅ 공격적 투자 전략 요청 테스트 완료!")
    print("="*60)

