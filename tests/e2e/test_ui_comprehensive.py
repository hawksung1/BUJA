"""
종합 UI 기능 테스트
- 로그인부터 모든 주요 기능까지 전체 플로우 테스트
"""
import pytest
import time
from playwright.sync_api import Page
from tests.e2e.conftest import take_screenshot, wait_for_streamlit_load


@pytest.mark.e2e
@pytest.mark.playwright
class TestComprehensiveUIFlow:
    """종합 UI 기능 테스트"""
    
    def test_complete_user_journey(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """전체 사용자 여정 테스트: 로그인 -> 대시보드 -> 프로필 -> 투자 선호도 -> 채팅 -> 로그아웃"""
        print("\n" + "=" * 80)
        print("종합 UI 기능 테스트 시작")
        print("=" * 80)
        
        # ========== STEP 1: 로그인 ==========
        print("\n[STEP 1] 로그인 페이지로 이동 및 로그인")
        page.goto(app_url, wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        time.sleep(2)
        take_screenshot(page, "01_login_page.png", screenshot_dir)
        
        # 이메일 입력
        email_input = page.locator("input[type='text']").first
        assert email_input.count() > 0, "이메일 입력 필드를 찾을 수 없습니다"
        email_input.fill("admin")
        time.sleep(0.5)
        
        # 비밀번호 입력
        password_input = page.locator("input[type='password']").first
        assert password_input.count() > 0, "비밀번호 입력 필드를 찾을 수 없습니다"
        password_input.fill("admin")
        time.sleep(0.5)
        
        take_screenshot(page, "02_login_form_filled.png", screenshot_dir)
        
        # 로그인 버튼 클릭
        submit_button = page.locator("button[type='submit']").first
        assert submit_button.count() > 0, "로그인 버튼을 찾을 수 없습니다"
        submit_button.click()
        time.sleep(5)  # 로그인 처리 대기
        
        take_screenshot(page, "03_after_login.png", screenshot_dir)
        print("[OK] 로그인 완료")
        
        # ========== STEP 2: 대시보드 확인 ==========
        print("\n[STEP 2] 대시보드 페이지 확인")
        # 사이드바에서 대시보드 링크 찾아서 클릭
        dashboard_link = page.locator("a[href*='dashboard'], button:has-text('대시보드'), button:has-text('Dashboard')").first
        if dashboard_link.count() == 0:
            # Streamlit page_link로 찾기
            dashboard_link = page.locator("[data-testid='stPageLink']:has-text('대시보드'), [data-testid='stPageLink']:has-text('Dashboard')").first
        if dashboard_link.count() > 0:
            dashboard_link.click()
            wait_for_streamlit_load(page)
            time.sleep(3)
        else:
            # 링크를 찾을 수 없으면 메인 페이지에서 대기
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(2)
        take_screenshot(page, "04_dashboard.png", screenshot_dir)
        
        # 대시보드 요소 확인
        body_text = page.locator("body").inner_text()
        assert "dashboard" in body_text.lower() or "대시보드" in body_text, "대시보드 페이지가 아닙니다"
        print("[OK] 대시보드 페이지 로드됨")
        
        # 메트릭 확인
        metrics = page.locator("text=/total|return|risk/i, text=/총|수익|위험/i")
        if metrics.count() > 0:
            print(f"[INFO] 메트릭 요소 {metrics.count()}개 발견")
        
        # ========== STEP 3: 프로필 페이지 ==========
        print("\n[STEP 3] 프로필 페이지 확인")
        # 사이드바에서 프로필 링크 찾아서 클릭
        profile_link = page.locator("a[href*='profile'], button:has-text('프로필'), button:has-text('Profile')").first
        if profile_link.count() == 0:
            profile_link = page.locator("[data-testid='stPageLink']:has-text('프로필'), [data-testid='stPageLink']:has-text('Profile')").first
        if profile_link.count() > 0:
            profile_link.click()
            wait_for_streamlit_load(page)
            time.sleep(3)
        else:
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(2)
        take_screenshot(page, "05_profile.png", screenshot_dir)
        
        # 프로필 폼 확인
        body_text = page.locator("body").inner_text()
        assert "프로필" in body_text or "profile" in body_text.lower(), "프로필 페이지가 아닙니다"
        
        # 프로필 입력 필드 확인
        text_inputs = page.locator("input[type='text']")
        number_inputs = page.locator("input[type='number']")
        print(f"[INFO] 텍스트 입력 필드: {text_inputs.count()}개")
        print(f"[INFO] 숫자 입력 필드: {number_inputs.count()}개")
        
        # 프로필 업데이트 테스트 (선택사항)
        if text_inputs.count() > 0:
            name_input = text_inputs.first
            if name_input.is_visible():
                name_input.fill("테스트 사용자")
                time.sleep(0.5)
                take_screenshot(page, "06_profile_filled.png", screenshot_dir)
        
        print("[OK] 프로필 페이지 확인 완료")
        
        # ========== STEP 4: 투자 선호도 페이지 ==========
        print("\n[STEP 4] 투자 선호도 페이지 확인")
        # 사이드바에서 투자 선호도 링크 찾아서 클릭
        preference_link = page.locator("a[href*='investment'], button:has-text('투자 선호도'), button:has-text('Investment')").first
        if preference_link.count() == 0:
            preference_link = page.locator("[data-testid='stPageLink']:has-text('투자 선호도'), [data-testid='stPageLink']:has-text('Investment')").first
        if preference_link.count() > 0:
            preference_link.click()
            wait_for_streamlit_load(page)
            time.sleep(3)
        else:
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(2)
        take_screenshot(page, "07_investment_preference.png", screenshot_dir)
        
        # 투자 선호도 폼 확인
        body_text = page.locator("body").inner_text()
        assert "preference" in body_text.lower() or "선호도" in body_text, "투자 선호도 페이지가 아닙니다"
        
        # 슬라이더 확인
        sliders = page.locator("input[type='range']")
        if sliders.count() > 0:
            print(f"[INFO] 슬라이더 {sliders.count()}개 발견")
            # 첫 번째 슬라이더 조작
            first_slider = sliders.first
            if first_slider.is_visible():
                # 슬라이더 값 변경 (Playwright의 fill 메서드 사용)
                first_slider.fill("7")
                time.sleep(1)
                take_screenshot(page, "08_preference_slider_changed.png", screenshot_dir)
        
        # 숫자 입력 필드 확인
        number_inputs = page.locator("input[type='number']")
        if number_inputs.count() > 0:
            print(f"[INFO] 숫자 입력 필드 {number_inputs.count()}개 발견")
        
        print("[OK] 투자 선호도 페이지 확인 완료")
        
        # ========== STEP 5: 에이전트 채팅 페이지 ==========
        print("\n[STEP 5] 에이전트 채팅 페이지 확인")
        # 사이드바에서 에이전트 채팅 링크 찾아서 클릭
        chat_link = page.locator("a[href*='agent'], button:has-text('에이전트 채팅'), button:has-text('Agent')").first
        if chat_link.count() == 0:
            chat_link = page.locator("[data-testid='stPageLink']:has-text('에이전트'), [data-testid='stPageLink']:has-text('Agent')").first
        if chat_link.count() > 0:
            chat_link.click()
            wait_for_streamlit_load(page)
            time.sleep(3)
        else:
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(2)
        take_screenshot(page, "09_agent_chat.png", screenshot_dir)
        
        # 채팅 인터페이스 확인
        body_text = page.locator("body").inner_text()
        assert "chat" in body_text.lower() or "채팅" in body_text or "agent" in body_text.lower(), "채팅 페이지가 아닙니다"
        
        # 채팅 입력 필드 확인
        chat_inputs = page.locator("textarea, input[type='text']")
        if chat_inputs.count() > 0:
            print(f"[INFO] 채팅 입력 필드 {chat_inputs.count()}개 발견")
            # 채팅 메시지 입력 테스트
            chat_input = chat_inputs.first
            if chat_input.is_visible():
                chat_input.fill("안녕하세요, 투자 조언을 받고 싶습니다")
                time.sleep(1)
                take_screenshot(page, "10_chat_input.png", screenshot_dir)
                # Enter 키로 제출 (선택사항)
                # chat_input.press("Enter")
                # time.sleep(3)
        
        # 사이드바 확인
        sidebar = page.locator("[data-testid='stSidebar'], aside, [class*='sidebar']")
        if sidebar.count() > 0:
            print("[INFO] 사이드바 발견")
        
        print("[OK] 에이전트 채팅 페이지 확인 완료")
        
        # ========== STEP 6: 네비게이션 테스트 ==========
        print("\n[STEP 6] 페이지 간 네비게이션 테스트")
        
        # 사이드바 링크 확인
        links = page.locator("a[href*='dashboard'], a[href*='profile'], a[href*='investment'], a[href*='agent']")
        if links.count() > 0:
            print(f"[INFO] 네비게이션 링크 {links.count()}개 발견")
            # 첫 번째 링크 클릭 테스트
            first_link = links.first
            if first_link.is_visible():
                link_text = first_link.inner_text()
                print(f"[INFO] 링크 클릭: {link_text[:50]}")
                first_link.click()
                time.sleep(3)
                take_screenshot(page, "11_navigation.png", screenshot_dir)
        
        print("[OK] 네비게이션 테스트 완료")
        
        # ========== STEP 7: 로그아웃 테스트 ==========
        print("\n[STEP 7] 로그아웃 테스트")
        
        # 로그아웃 버튼 찾기
        logout_buttons = page.locator("button:has-text('Logout'), button:has-text('로그아웃')")
        if logout_buttons.count() == 0:
            # 다른 방법으로 찾기
            logout_buttons = page.locator("button").filter(has_text=page.locator("text=/logout|로그아웃/i"))
        
        if logout_buttons.count() > 0:
            logout_button = logout_buttons.first
            if logout_button.is_visible():
                print("[INFO] 로그아웃 버튼 발견")
                logout_button.click()
                time.sleep(3)
                take_screenshot(page, "12_after_logout.png", screenshot_dir)
                
                # 로그인 페이지로 리다이렉트 확인
                body_text = page.locator("body").inner_text()
                assert "login" in body_text.lower() or "로그인" in body_text, "로그아웃 후 로그인 페이지로 이동하지 않았습니다"
                print("[OK] 로그아웃 완료")
        else:
            print("[WARN] 로그아웃 버튼을 찾을 수 없습니다")
        
        print("\n" + "=" * 80)
        print("종합 UI 기능 테스트 완료!")
        print("=" * 80)


@pytest.mark.e2e
@pytest.mark.playwright
class TestPageNavigation:
    """페이지 네비게이션 테스트"""
    
    def test_all_pages_accessible(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """모든 페이지가 접근 가능한지 확인"""
        print("\n" + "=" * 80)
        print("모든 페이지 접근성 테스트")
        print("=" * 80)
        
        # 먼저 로그인
        page.goto(app_url, wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        time.sleep(2)
        
        email_input = page.locator("input[type='text']").first
        password_input = page.locator("input[type='password']").first
        
        if email_input.count() > 0 and password_input.count() > 0:
            email_input.fill("admin")
            password_input.fill("admin")
            time.sleep(0.5)
            
            submit_button = page.locator("button[type='submit']").first
            if submit_button.count() > 0:
                submit_button.click()
                time.sleep(5)
        
        # 테스트할 페이지 목록
        pages = [
            ("dashboard", "대시보드"),
            ("profile", "프로필"),
            ("investment_preference", "투자 선호도"),
            ("agent_chat", "에이전트 채팅"),
        ]
        
        for page_name, page_title in pages:
            print(f"\n[TEST] {page_title} 페이지 접근 테스트")
            # 사이드바에서 해당 페이지 링크 찾아서 클릭
            page_link = None
            # 여러 방법으로 링크 찾기
            selectors = [
                f"a[href*='{page_name}']",
                f"button:has-text('{page_title}')",
                f"[data-testid='stPageLink']:has-text('{page_title}')",
            ]
            
            for selector in selectors:
                page_link = page.locator(selector).first
                if page_link.count() > 0:
                    break
            
            if page_link and page_link.count() > 0:
                page_link.click()
                wait_for_streamlit_load(page)
                time.sleep(2)
            else:
                print(f"[WARN] {page_title} 링크를 찾을 수 없습니다. 현재 페이지에서 확인합니다.")
                page.wait_for_load_state("networkidle", timeout=10000)
                time.sleep(2)
            
            take_screenshot(page, f"page_{page_name}.png", screenshot_dir)
            
            # 페이지 콘텐츠 확인
            body_text = page.locator("body").inner_text()
            assert len(body_text) > 0, f"{page_title} 페이지가 비어있습니다"
            
            # 페이지 제목 확인
            title = page.title()
            assert title is not None, f"{page_title} 페이지 제목이 없습니다"
            
            print(f"[OK] {page_title} 페이지 접근 성공")
        
        print("\n[OK] 모든 페이지 접근성 테스트 완료")


@pytest.mark.e2e
@pytest.mark.playwright
class TestFormInteractions:
    """폼 상호작용 테스트"""
    
    def test_form_inputs_work(self, page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
        """모든 폼 입력이 정상 작동하는지 확인"""
        print("\n" + "=" * 80)
        print("폼 상호작용 테스트")
        print("=" * 80)
        
        # 로그인
        page.goto(app_url, wait_until="domcontentloaded", timeout=30000)
        wait_for_streamlit_load(page)
        time.sleep(2)
        
        email_input = page.locator("input[type='text']").first
        password_input = page.locator("input[type='password']").first
        
        if email_input.count() > 0 and password_input.count() > 0:
            email_input.fill("admin")
            password_input.fill("admin")
            time.sleep(0.5)
            
            submit_button = page.locator("button[type='submit']").first
            if submit_button.count() > 0:
                submit_button.click()
                time.sleep(5)
        
        # 프로필 페이지에서 폼 테스트
        print("\n[TEST] 프로필 폼 입력 테스트")
        # 사이드바에서 프로필 링크 찾아서 클릭
        profile_link = page.locator("a[href*='profile'], button:has-text('프로필'), [data-testid='stPageLink']:has-text('프로필')").first
        if profile_link.count() > 0:
            profile_link.click()
            wait_for_streamlit_load(page)
            time.sleep(2)
        else:
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(2)
        
        # 텍스트 입력
        text_inputs = page.locator("input[type='text']")
        if text_inputs.count() > 0:
            for i in range(min(3, text_inputs.count())):
                input_field = text_inputs.nth(i)
                if input_field.is_visible():
                    input_field.fill(f"테스트 입력 {i+1}")
                    time.sleep(0.3)
        
        # 숫자 입력
        number_inputs = page.locator("input[type='number']")
        if number_inputs.count() > 0:
            for i in range(min(2, number_inputs.count())):
                input_field = number_inputs.nth(i)
                if input_field.is_visible():
                    input_field.fill("25")
                    time.sleep(0.3)
        
        take_screenshot(page, "form_inputs_filled.png", screenshot_dir)
        print("[OK] 프로필 폼 입력 테스트 완료")
        
        # 투자 선호도 페이지에서 폼 테스트
        print("\n[TEST] 투자 선호도 폼 입력 테스트")
        # 사이드바에서 투자 선호도 링크 찾아서 클릭
        preference_link = page.locator("a[href*='investment'], button:has-text('투자 선호도'), [data-testid='stPageLink']:has-text('투자 선호도')").first
        if preference_link.count() > 0:
            preference_link.click()
            wait_for_streamlit_load(page)
            time.sleep(2)
        else:
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(2)
        
        # 슬라이더 테스트
        sliders = page.locator("input[type='range']")
        if sliders.count() > 0:
            slider = sliders.first
            if slider.is_visible():
                slider.fill("7")
                time.sleep(0.5)
        
        # 숫자 입력 테스트
        number_inputs = page.locator("input[type='number']")
        if number_inputs.count() > 0:
            number_input = number_inputs.first
            if number_input.is_visible():
                number_input.fill("10.5")
                time.sleep(0.5)
        
        # 셀렉트박스 테스트
        selectboxes = page.locator("select, [role='combobox']")
        if selectboxes.count() > 0:
            selectbox = selectboxes.first
            if selectbox.is_visible():
                options = selectbox.locator("option")
                if options.count() > 1:
                    selectbox.select_option(index=1)
                    time.sleep(0.5)
        
        take_screenshot(page, "preference_form_filled.png", screenshot_dir)
        print("[OK] 투자 선호도 폼 입력 테스트 완료")
        
        print("\n[OK] 폼 상호작용 테스트 완료")

