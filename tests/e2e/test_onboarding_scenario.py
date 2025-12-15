"""
온보딩 시나리오 E2E 테스트
USER_SCENARIO.md의 2단계 온보딩 프로세스를 테스트
"""
import time

import pytest
from playwright.sync_api import Page

from tests.e2e.conftest import take_screenshot, wait_for_streamlit_load


def test_onboarding_complete_flow(page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
    """온보딩 전체 플로우 테스트 (간소화된 2단계)
    
    시나리오:
    - Step 1: 기본 정보 입력 (이름, 나이, 직업 선택)
    - Step 2: 투자 목표 (시작 자산, 목표 수익률, 위험 감수 성향, 월 투자 가능액)
    """

    print("\n" + "="*60)
    print("온보딩 시나리오 테스트 시작")
    print("="*60)

    # ============================================================
    # 사전 준비: 회원가입 및 로그인
    # ============================================================
    print("\n[사전 준비] 회원가입 및 로그인")
    page.goto(f"{app_url}/login", wait_until="domcontentloaded", timeout=30000)
    wait_for_streamlit_load(page)
    time.sleep(2)

    # 회원가입 탭으로 전환
    try:
        register_tab = page.get_by_text("📝 Register")
        if register_tab.count() > 0:
            register_tab.click()
            time.sleep(1)
    except Exception as e:
        print(f"[WARN] Register 탭 클릭 실패: {e}")

    # 회원가입 정보 입력
    try:
        # 고유한 이메일 생성 (타임스탬프 사용)
        import random
        test_email = f"test_onboarding_{int(time.time())}_{random.randint(1000, 9999)}@example.com"
        
        # 이메일 입력
        email_inputs = page.locator("input[type='text']")
        for inp in email_inputs.all():
            if inp.is_visible():
                placeholder = inp.get_attribute('placeholder') or ''
                if 'email' in placeholder.lower():
                    inp.fill(test_email)
                    break
        
        # 비밀번호 입력
        password_inputs = page.locator("input[type='password']")
        if password_inputs.count() >= 2:
            password_inputs.nth(0).fill("securePass123!")
            password_inputs.nth(1).fill("securePass123!")
        
        # 이름, 나이, 직업 입력
        text_inputs = page.locator("input[type='text']")
        for inp in text_inputs.all():
            if inp.is_visible():
                placeholder = inp.get_attribute('placeholder') or ''
                if 'name' in placeholder.lower() or '이름' in placeholder:
                    inp.fill("김철수")
                elif 'age' in placeholder.lower() or '나이' in placeholder:
                    inp.fill("32")
                elif 'occupation' in placeholder.lower() or '직업' in placeholder:
                    inp.fill("IT 개발자")
        
        # 회원가입 버튼 클릭
        register_button = page.locator("button[type='submit']").first
        if register_button.count() > 0:
            register_button.click()
            time.sleep(3)
            take_screenshot(page, "01_after_register.png", screenshot_dir)
    except Exception as e:
        print(f"[WARN] 회원가입 실패: {e}")
        pytest.skip("회원가입 실패 - 온보딩 테스트 스킵")

    # ============================================================
    # Step 1: 기본 정보 입력 (온보딩)
    # ============================================================
    print("\n[Step 1] 온보딩 - 기본 정보 입력")
    
    # 온보딩 페이지로 이동 (자동 리다이렉트 또는 수동 이동)
    current_url = page.url
    if "onboarding" not in current_url.lower():
        page.goto(f"{app_url}/onboarding", wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        time.sleep(2)
    
    take_screenshot(page, "02_onboarding_step1.png", screenshot_dir)
    
    # 진행 바 확인 (간소화된 2단계)
    progress_text = page.locator("text=/1\\/2|Step 1/").first
    if progress_text.count() > 0:
        print("[OK] 진행 바 확인: 1/2 단계")
    
    # 기본 정보는 이미 입력되어 있을 수 있음 (회원가입 시 입력)
    # "다음" 버튼 클릭
    next_button = page.get_by_text("다음")
    if next_button.count() == 0:
        next_button = page.get_by_text("Next")
    
    if next_button.count() > 0:
        next_button.click()
        time.sleep(2)
        take_screenshot(page, "03_onboarding_step2.png", screenshot_dir)
        print("[OK] Step 1 완료 - Step 2로 이동")
    else:
        print("[WARN] '다음' 버튼을 찾을 수 없습니다")

    # ============================================================
    # Step 2: 투자 목표 입력 (간소화된 버전)
    # ============================================================
    print("\n[Step 2] 온보딩 - 투자 목표 입력")
    
    # 진행 바 확인
    progress_text = page.locator("text=/2\\/2|Step 2/").first
    if progress_text.count() > 0:
        print("[OK] 진행 바 확인: 2/2 단계")
    
    # 투자 목표 정보 입력
    try:
        # 필수 필드: 시작 자산, 목표 수익률, 위험 감수 성향
        # 선택 필드: 월 투자 가능액
        
        # 시작 자산 입력 (2천만원)
        assets_input = page.locator("text=/시작 자산/").first
        if assets_input.count() > 0:
            # label 근처의 input 찾기
            parent = assets_input.locator("xpath=ancestor::div[1]")
            input_field = parent.locator("input[type='number']").first
            if input_field.count() > 0:
                input_field.fill("20000000")
                print("[INFO] 시작 자산: 20,000,000원 입력")
        
        # 월 투자 가능액 입력 (200만원)
        monthly_investment_input = page.locator("text=/월 투자 가능액/").first
        if monthly_investment_input.count() > 0:
            parent = monthly_investment_input.locator("xpath=ancestor::div[1]")
            input_field = parent.locator("input[type='number']").first
            if input_field.count() > 0:
                input_field.fill("2000000")
                print("[INFO] 월 투자 가능액: 2,000,000원 입력")
        
        # 목표 수익률 입력 (10%)
        target_return_input = page.locator("text=/목표 수익률/").first
        if target_return_input.count() > 0:
            parent = target_return_input.locator("xpath=ancestor::div[1]")
            input_field = parent.locator("input[type='number']").first
            if input_field.count() > 0:
                input_field.fill("10.0")
                print("[INFO] 목표 수익률: 10.0% 입력")
        
        # 위험 감수 성향 슬라이더 (5 선택)
        risk_slider = page.locator("input[type='range']").first
        if risk_slider.count() > 0:
            risk_slider.fill("5")
            print("[INFO] 위험 감수 성향: 5 선택")
        
        time.sleep(1)
        take_screenshot(page, "04_investment_goal_filled.png", screenshot_dir)
        
        # "완료하고 포트폴리오 받기" 버튼 클릭
        complete_button = page.get_by_text("완료하고 포트폴리오 받기")
        if complete_button.count() == 0:
            complete_button = page.get_by_text("완료", exact=False)
        if complete_button.count() == 0:
            complete_button = page.get_by_text("Complete")
        
        if complete_button.count() > 0:
            complete_button.click()
            time.sleep(3)
            take_screenshot(page, "05_onboarding_completed.png", screenshot_dir)
            print("[OK] Step 2 완료 - 온보딩 완료!")
    except Exception as e:
        print(f"[WARN] 투자 목표 입력 실패: {e}")

    # ============================================================
    # 검증: Agent Chat으로 리다이렉트 확인
    # ============================================================
    print("\n[검증] Agent Chat으로 리다이렉트 확인")
    time.sleep(2)
    current_url = page.url
    
    # Agent Chat 또는 Dashboard로 이동했는지 확인
    assert "agent_chat" in current_url.lower() or "dashboard" in current_url.lower(), \
        f"온보딩 완료 후 리다이렉트 실패: {current_url}"
    
    print(f"[OK] 온보딩 완료 후 리다이렉트 성공: {current_url}")

    print("\n" + "="*60)
    print("[OK] 온보딩 시나리오 테스트 완료!")
    print("="*60)
