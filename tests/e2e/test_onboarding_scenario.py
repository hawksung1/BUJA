"""
온보딩 시나리오 E2E 테스트
USER_SCENARIO.md의 2단계 온보딩 프로세스를 테스트
"""
import time

import pytest
from playwright.sync_api import Page

from tests.e2e.conftest import take_screenshot, wait_for_streamlit_load


def test_onboarding_complete_flow(page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
    """온보딩 전체 플로우 테스트
    
    시나리오:
    - Step 1: 기본 정보 입력
    - Step 2: 재무 상황 입력
    - Step 3: 투자 성향 설정
    - Step 4: 재무 목표 설정
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
    
    # 진행 바 확인
    progress_text = page.locator("text=/1\\/4|Step 1/").first
    if progress_text.count() > 0:
        print("[✅] 진행 바 확인: 1/4 단계")
    
    # 기본 정보는 이미 입력되어 있을 수 있음 (회원가입 시 입력)
    # "다음" 버튼 클릭
    next_button = page.get_by_text("다음")
    if next_button.count() == 0:
        next_button = page.get_by_text("Next")
    
    if next_button.count() > 0:
        next_button.click()
        time.sleep(2)
        take_screenshot(page, "03_onboarding_step2.png", screenshot_dir)
        print("[✅] Step 1 완료 - Step 2로 이동")
    else:
        print("[WARN] '다음' 버튼을 찾을 수 없습니다")

    # ============================================================
    # Step 2: 재무 상황 입력
    # ============================================================
    print("\n[Step 2] 온보딩 - 재무 상황 입력")
    
    # 진행 바 확인
    progress_text = page.locator("text=/2\\/4|Step 2/").first
    if progress_text.count() > 0:
        print("[✅] 진행 바 확인: 2/4 단계")
    
    # 재무 정보 입력
    try:
        # number_input 필드 찾기
        number_inputs = page.locator("input[type='number']")
        
        # 월 소득, 월 지출, 총 자산 등 입력
        # Streamlit의 number_input은 label과 연결되어 있음
        financial_data = {
            "월 소득": "5000000",
            "월 지출": "3500000",
            "총 자산": "50000000",
            "총 부채": "30000000",
            "비상금": "15000000",
            "가족 구성원": "2",
            "보험 보장액": "100000000"
        }
        
        for label_text, value in financial_data.items():
            try:
                # label을 찾고 연결된 input 찾기
                label = page.locator(f"text=/{label_text}/").first
                if label.count() > 0:
                    # label 근처의 input 찾기
                    parent = label.locator("xpath=ancestor::div[1]")
                    input_field = parent.locator("input[type='number']").first
                    if input_field.count() > 0:
                        input_field.fill(value)
                        print(f"[INFO] {label_text}: {value} 입력")
            except Exception as e:
                print(f"[WARN] {label_text} 입력 실패: {e}")
        
        time.sleep(1)
        take_screenshot(page, "04_financial_info_filled.png", screenshot_dir)
        
        # "다음" 버튼 클릭
        next_button = page.get_by_text("다음")
        if next_button.count() == 0:
            next_button = page.get_by_text("Next")
        
        if next_button.count() > 0:
            next_button.click()
            time.sleep(2)
            take_screenshot(page, "05_onboarding_step3.png", screenshot_dir)
            print("[✅] Step 2 완료 - Step 3으로 이동")
    except Exception as e:
        print(f"[WARN] 재무 정보 입력 실패: {e}")

    # ============================================================
    # Step 3: 투자 성향 설정
    # ============================================================
    print("\n[Step 3] 온보딩 - 투자 성향 설정")
    
    # 진행 바 확인
    progress_text = page.locator("text=/3\\/4|Step 3/").first
    if progress_text.count() > 0:
        print("[✅] 진행 바 확인: 3/4 단계")
    
    try:
        # 위험 감수 성향 슬라이더 (5 선택)
        # Streamlit slider는 input[type='range']로 렌더링됨
        risk_slider = page.locator("input[type='range']").first
        if risk_slider.count() > 0:
            risk_slider.fill("5")
            print("[INFO] 위험 감수 성향: 5 선택")
        
        # 목표 수익률 입력 (8.0%)
        target_return_input = page.locator("input[type='number']").first
        if target_return_input.count() > 0:
            target_return_input.fill("8.0")
            print("[INFO] 목표 수익률: 8.0% 입력")
        
        # 투자 기간 선택 (MEDIUM)
        # Streamlit selectbox는 select 태그로 렌더링됨
        period_select = page.locator("select").first
        if period_select.count() > 0:
            period_select.select_option(label="MEDIUM")
            print("[INFO] 투자 기간: MEDIUM 선택")
        
        # 투자 경험 선택 (BEGINNER)
        experience_select = page.locator("select").nth(1)
        if experience_select.count() > 0:
            experience_select.select_option(label="BEGINNER")
            print("[INFO] 투자 경험: BEGINNER 선택")
        
        # 최대 손실 허용 범위 입력 (15.0%)
        max_loss_input = page.locator("input[type='number']").nth(1)
        if max_loss_input.count() > 0:
            max_loss_input.fill("15.0")
            print("[INFO] 최대 손실 허용 범위: 15.0% 입력")
        
        time.sleep(1)
        take_screenshot(page, "06_investment_preference_filled.png", screenshot_dir)
        
        # "다음" 버튼 클릭
        next_button = page.get_by_text("다음")
        if next_button.count() == 0:
            next_button = page.get_by_text("Next")
        
        if next_button.count() > 0:
            next_button.click()
            time.sleep(2)
            take_screenshot(page, "07_onboarding_step4.png", screenshot_dir)
            print("[✅] Step 3 완료 - Step 4로 이동")
    except Exception as e:
        print(f"[WARN] 투자 성향 입력 실패: {e}")

    # ============================================================
    # Step 4: 재무 목표 설정
    # ============================================================
    print("\n[Step 4] 온보딩 - 재무 목표 설정")
    
    # 진행 바 확인
    progress_text = page.locator("text=/4\\/4|Step 4/").first
    if progress_text.count() > 0:
        print("[✅] 진행 바 확인: 4/4 단계")
    
    try:
        # 목표 유형 선택 (주택 구매)
        goal_type_select = page.locator("select").first
        if goal_type_select.count() > 0:
            # 옵션 확인
            options = goal_type_select.locator("option").all()
            for option in options:
                if "주택" in option.text_content() or "HOUSE" in option.text_content():
                    option.click()
                    print("[INFO] 목표 유형: 주택 구매 선택")
                    break
        
        # 목표 금액 입력 (3억원)
        goal_amount_input = page.locator("input[type='number']").first
        if goal_amount_input.count() > 0:
            goal_amount_input.fill("300000000")
            print("[INFO] 목표 금액: 300,000,000원 입력")
        
        # 목표 날짜 선택 (5년 후)
        # Streamlit date_input은 input[type='date']로 렌더링됨
        from datetime import datetime, timedelta
        target_date = (datetime.now() + timedelta(days=365*5)).strftime("%Y-%m-%d")
        date_input = page.locator("input[type='date']").first
        if date_input.count() > 0:
            date_input.fill(target_date)
            print(f"[INFO] 목표 날짜: {target_date} 입력")
        
        # 우선순위 선택 (1)
        priority_slider = page.locator("input[type='range']").first
        if priority_slider.count() > 0:
            priority_slider.fill("1")
            print("[INFO] 우선순위: 1 선택")
        
        time.sleep(1)
        take_screenshot(page, "08_financial_goal_filled.png", screenshot_dir)
        
        # "목표 추가" 버튼 클릭
        add_goal_button = page.get_by_text("목표 추가")
        if add_goal_button.count() == 0:
            add_goal_button = page.get_by_text("Add Goal")
        
        if add_goal_button.count() > 0:
            add_goal_button.click()
            time.sleep(2)
            take_screenshot(page, "09_goal_added.png", screenshot_dir)
            print("[✅] 재무 목표 추가 완료")
        
        # "완료" 버튼 클릭
        complete_button = page.get_by_text("완료")
        if complete_button.count() == 0:
            complete_button = page.get_by_text("Complete")
        
        if complete_button.count() > 0:
            complete_button.click()
            time.sleep(3)
            take_screenshot(page, "10_onboarding_completed.png", screenshot_dir)
            print("[✅] 온보딩 완료!")
    except Exception as e:
        print(f"[WARN] 재무 목표 입력 실패: {e}")

    # ============================================================
    # 검증: Agent Chat으로 리다이렉트 확인
    # ============================================================
    print("\n[검증] Agent Chat으로 리다이렉트 확인")
    time.sleep(2)
    current_url = page.url
    
    # Agent Chat 또는 Dashboard로 이동했는지 확인
    assert "agent_chat" in current_url.lower() or "dashboard" in current_url.lower(), \
        f"온보딩 완료 후 리다이렉트 실패: {current_url}"
    
    print(f"[✅] 온보딩 완료 후 리다이렉트 성공: {current_url}")

    print("\n" + "="*60)
    print("✅ 온보딩 시나리오 테스트 완료!")
    print("="*60)
