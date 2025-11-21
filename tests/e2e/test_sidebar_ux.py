"""
사이드바 UX 개선 확인 스크립트
Playwright를 사용하여 실제 UI를 확인합니다.
"""
import asyncio
import io
import sys

from playwright.async_api import async_playwright

# Windows 콘솔 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


async def test_sidebar_ux():
    """사이드바 UX 개선 상태를 확인합니다."""
    async with async_playwright() as p:
        print("=" * 80)
        print("사이드바 UX 개선 확인 테스트")
        print("=" * 80)

        # 브라우저 실행
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        try:
            # 1. 비로그인 상태 확인
            print("\n[테스트 1] 비로그인 상태 - Login 페이지")
            print("-" * 80)
            await page.goto("http://localhost:8501/login", wait_until="networkidle")
            await page.wait_for_timeout(2000)  # Streamlit 렌더링 대기

            # 스크린샷 저장
            await page.screenshot(path="test_sidebar_unauthenticated.png", full_page=True)
            print("✓ 스크린샷 저장: test_sidebar_unauthenticated.png")

            # 사이드바 내용 확인
            sidebar = page.locator('[data-testid="stSidebar"]')
            if await sidebar.count() > 0:
                sidebar_text = await sidebar.inner_text()
                print(f"\n사이드바 내용:\n{sidebar_text[:500]}...")

                # 기본 네비게이션이 숨겨졌는지 확인
                nav_menu = page.locator('[data-testid="stSidebarNav"]')
                nav_count = await nav_menu.count()
                if nav_count == 0:
                    print("✓ 기본 네비게이션 메뉴가 숨겨졌습니다.")
                else:
                    print("✗ 기본 네비게이션 메뉴가 여전히 표시됩니다.")

                # 커스텀 사이드바 요소 확인
                if "BUJA" in sidebar_text:
                    print("✓ 커스텀 사이드바가 표시됩니다.")
                else:
                    print("✗ 커스텀 사이드바가 표시되지 않습니다.")

                # Login, Register 링크 확인
                if "Login" in sidebar_text or "로그인" in sidebar_text:
                    print("✓ Login 링크가 표시됩니다.")
                else:
                    print("✗ Login 링크가 표시되지 않습니다.")

                if "Register" in sidebar_text or "회원가입" in sidebar_text:
                    print("✓ Register 링크가 표시됩니다.")
                else:
                    print("✗ Register 링크가 표시되지 않습니다.")

                # 다른 메뉴가 보이지 않는지 확인
                unwanted_items = ["agent chat", "dashboard", "profile", "mcp tools"]
                found_unwanted = []
                for item in unwanted_items:
                    if item.lower() in sidebar_text.lower():
                        found_unwanted.append(item)

                if found_unwanted:
                    print(f"✗ 비로그인 상태에서 보이면 안 되는 메뉴: {', '.join(found_unwanted)}")
                else:
                    print("✓ 비로그인 상태에서 불필요한 메뉴가 표시되지 않습니다.")
            else:
                print("✗ 사이드바를 찾을 수 없습니다.")

            # 2. 로그인 후 상태 확인
            print("\n[테스트 2] 로그인 상태 확인")
            print("-" * 80)

            # 로그인 시도
            try:
                # Login 탭이 있는지 확인
                login_tab = page.locator('button[role="tab"]:has-text("Login"), button:has-text("로그인")').first
                if await login_tab.count() > 0:
                    await login_tab.click()
                    await page.wait_for_timeout(500)

                # 입력 필드 찾기
                email_input = page.locator('input[placeholder*="email" i], input[type="text"]').first
                password_input = page.locator('input[type="password"]').first
                login_button = page.locator('button[type="submit"]:has-text("Login"), button:has-text("로그인"), button:has-text("Login")').first

                if await email_input.count() > 0 and await password_input.count() > 0:
                    print("✓ 로그인 폼을 찾았습니다.")
                    await email_input.fill("admin")
                    await password_input.fill("admin")
                    await page.wait_for_timeout(500)

                    # 로그인 버튼 클릭
                    if await login_button.count() > 0:
                        await login_button.click()
                        print("✓ 로그인 버튼 클릭")
                    else:
                        # form submit 시도
                        await email_input.press("Enter")
                        print("✓ Enter 키로 로그인 시도")

                    # 로그인 처리 대기 (최대 5초)
                    await page.wait_for_timeout(5000)

                    # 현재 URL 확인
                    current_url = page.url
                    print(f"현재 URL: {current_url}")

                    # 로그인 성공 여부 확인
                    if "login" not in current_url.lower() or "agent_chat" in current_url.lower() or "onboarding" in current_url.lower():
                        print("✓ 로그인 성공 또는 리다이렉트됨")

                        # 페이지가 완전히 로드될 때까지 대기
                        await page.wait_for_load_state("networkidle", timeout=10000)
                        await page.wait_for_timeout(3000)

                        # 로그인 후 사이드바 확인
                        sidebar_after_login = page.locator('[data-testid="stSidebar"]')
                        if await sidebar_after_login.count() > 0:
                            sidebar_text_after = await sidebar_after_login.inner_text()
                            print("\n로그인 후 사이드바 전체 내용:")
                            print("-" * 80)
                            print(sidebar_text_after)
                            print("-" * 80)

                            # 기본 네비게이션이 숨겨졌는지 확인
                            nav_menu_after = page.locator('[data-testid="stSidebarNav"]')
                            nav_count_after = await nav_menu_after.count()
                            if nav_count_after == 0:
                                print("✓ 로그인 후에도 기본 네비게이션 메뉴가 숨겨져 있습니다.")
                            else:
                                print("✗ 로그인 후 기본 네비게이션 메뉴가 여전히 표시됩니다.")

                            # 커스텀 사이드바 요소 확인
                            if "BUJA" in sidebar_text_after:
                                print("✓ 커스텀 사이드바가 표시됩니다.")
                            else:
                                print("✗ 커스텀 사이드바가 표시되지 않습니다.")

                            # 사용자 이메일 표시 확인
                            if "admin" in sidebar_text_after.lower():
                                print("✓ 사용자 이메일(admin)이 표시됩니다.")
                            else:
                                print("✗ 사용자 이메일이 표시되지 않습니다.")

                            # 온보딩 상태 확인
                            has_onboarding = "온보딩" in sidebar_text_after or "onboarding" in sidebar_text_after.lower()
                            if has_onboarding:
                                print("✓ 온보딩 관련 메뉴가 표시됩니다.")

                                # 온보딩 미완료 상태 확인
                                if "미완료" in sidebar_text_after or "필요" in sidebar_text_after:
                                    print("  → 온보딩 미완료 상태로 표시됩니다.")
                                elif "완료" in sidebar_text_after:
                                    print("  → 온보딩 완료 상태로 표시됩니다.")
                            else:
                                print("⚠ 온보딩 관련 메뉴가 표시되지 않습니다.")

                            # 메인 메뉴 확인
                            if "메인 메뉴" in sidebar_text_after or "메뉴" in sidebar_text_after:
                                print("✓ 메인 메뉴 섹션이 표시됩니다.")

                            # Agent Chat 메뉴 확인
                            has_agent_chat = "agent chat" in sidebar_text_after.lower() or "Agent Chat" in sidebar_text_after
                            if has_agent_chat:
                                print("✓ Agent Chat 메뉴가 표시됩니다.")
                            else:
                                print("✗ Agent Chat 메뉴가 표시되지 않습니다.")

                            # Dashboard 메뉴 확인
                            has_dashboard = "dashboard" in sidebar_text_after.lower() or "Dashboard" in sidebar_text_after
                            if has_dashboard:
                                print("✓ Dashboard 메뉴가 표시됩니다.")
                            else:
                                print("✗ Dashboard 메뉴가 표시되지 않습니다.")

                            # 설정 메뉴 확인
                            has_settings = "설정" in sidebar_text_after or "Settings" in sidebar_text_after
                            if has_settings:
                                print("✓ 설정 메뉴 섹션이 표시됩니다.")

                            # Profile 메뉴 확인
                            has_profile = "profile" in sidebar_text_after.lower() or "Profile" in sidebar_text_after
                            if has_profile:
                                print("✓ Profile 메뉴가 표시됩니다.")

                            # MCP Tools 메뉴 확인
                            has_mcp = "mcp" in sidebar_text_after.lower() or "MCP" in sidebar_text_after
                            if has_mcp:
                                print("✓ MCP Tools 메뉴가 표시됩니다.")

                            # Logout 버튼 확인
                            has_logout = "logout" in sidebar_text_after.lower() or "Logout" in sidebar_text_after or "로그아웃" in sidebar_text_after
                            if has_logout:
                                print("✓ Logout 버튼이 표시됩니다.")
                            else:
                                print("✗ Logout 버튼이 표시되지 않습니다.")

                            # 비로그인 상태에서 보이면 안 되는 메뉴 확인
                            login_register_after = "Login" in sidebar_text_after or "Register" in sidebar_text_after or "로그인" in sidebar_text_after or "회원가입" in sidebar_text_after
                            if login_register_after:
                                print("⚠ 로그인 후에도 Login/Register 메뉴가 표시됩니다. (제거 필요)")
                            else:
                                print("✓ 로그인 후 Login/Register 메뉴가 제거되었습니다.")

                            await page.screenshot(path="test_sidebar_authenticated.png", full_page=True)
                            print("\n✓ 스크린샷 저장: test_sidebar_authenticated.png")
                        else:
                            print("✗ 로그인 후 사이드바를 찾을 수 없습니다.")
                    else:
                        print("⚠ 로그인 페이지에 머물러 있습니다.")
                        print("  → 로그인 실패 또는 autologin이 비활성화되어 있을 수 있습니다.")
                else:
                    print("⚠ 로그인 폼을 찾을 수 없습니다.")
                    print("  → autologin이 활성화되어 있거나 이미 로그인된 상태일 수 있습니다.")

                    # 이미 로그인된 상태인지 확인
                    current_url = page.url
                    if "login" not in current_url.lower():
                        print("  → 이미 다른 페이지에 있습니다. 사이드바 확인을 진행합니다.")
                        await page.wait_for_timeout(2000)
                        sidebar_check = page.locator('[data-testid="stSidebar"]')
                        if await sidebar_check.count() > 0:
                            sidebar_text_check = await sidebar_check.inner_text()
                            print(f"\n현재 페이지 사이드바 내용:\n{sidebar_text_check[:500]}...")
                            await page.screenshot(path="test_sidebar_current.png", full_page=True)
                            print("✓ 스크린샷 저장: test_sidebar_current.png")
            except Exception as e:
                print(f"⚠ 로그인 테스트 중 오류: {e}")
                import traceback
                traceback.print_exc()

            print("\n" + "=" * 80)
            print("테스트 완료")
            print("=" * 80)

        except Exception as e:
            print(f"\n✗ 오류 발생: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()


def test_file_upload_icon_in_chat_input(page: Page, app_url: str, ensure_app_running, screenshot_dir: str):
    """채팅 입력창 내부에 파일 업로드 아이콘이 있는지 확인"""
    print("\n" + "="*60)
    print("파일 업로드 아이콘 테스트 시작")
    print("="*60)

    # Step 1: 로그인
    print("\n[Step 1] 로그인")
    page.goto(f"{app_url}/login", wait_until="domcontentloaded", timeout=30000)
    wait_for_streamlit_load(page)

    try:
        email_input = page.locator("input[type='text']").first
        password_input = page.locator("input[type='password']").first

        if email_input.count() > 0 and password_input.count() > 0:
            email_input.fill("admin@example.com")
            password_input.fill("admin123")
            page.locator("button:has-text('Login')").first.click()
            time.sleep(3)
    except Exception as e:
        print(f"[WARN] 로그인 시도 중 오류: {e}")

    # Step 2: Agent Chat 페이지로 이동
    print("\n[Step 2] Agent Chat 페이지로 이동")
    page.goto(f"{app_url}/Agent_Chat", wait_until="domcontentloaded", timeout=30000)
    wait_for_streamlit_load(page)
    time.sleep(5)  # CSS/JS 적용 대기

    # 전체 페이지 스크린샷
    take_screenshot(page, "file_upload_icon_full.png", screenshot_dir)

    # Step 3: 파일 업로드 아이콘 확인
    print("\n[Step 3] 파일 업로드 아이콘 확인")

    # 여러 방법으로 아이콘 찾기
    upload_icon = page.locator("#chat-file-upload-icon")
    if upload_icon.count() == 0:
        upload_icon = page.locator("#file-upload-icon-btn")
    if upload_icon.count() == 0:
        upload_icon = page.locator("#file-upload-icon-wrapper")

    icon_box = None

    # file-upload-icon-wrapper 확인
    wrapper = page.locator("#file-upload-icon-wrapper")
    if wrapper.count() > 0:
        print("  [OK] file-upload-icon-wrapper 발견!")
        wrapper_box = wrapper.bounding_box()
        if wrapper_box:
            print(f"  Wrapper 위치: x={wrapper_box['x']:.2f}, y={wrapper_box['y']:.2f}")

    if upload_icon.count() > 0:
        print("[OK] 파일 업로드 아이콘 발견!")

        # 아이콘 위치 확인
        icon_box = upload_icon.bounding_box()
        if icon_box:
            print(f"  아이콘 위치: x={icon_box['x']:.2f}, y={icon_box['y']:.2f}, width={icon_box['width']:.2f}, height={icon_box['height']:.2f}")

        # 아이콘 스타일 확인
        display = upload_icon.evaluate("el => window.getComputedStyle(el).display")
        visibility = upload_icon.evaluate("el => window.getComputedStyle(el).visibility")
        opacity = upload_icon.evaluate("el => window.getComputedStyle(el).opacity")
        print(f"  아이콘 display: {display}")
        print(f"  아이콘 visibility: {visibility}")
        print(f"  아이콘 opacity: {opacity}")

        if display == "none" or visibility == "hidden" or opacity == "0":
            print("[WARN] 아이콘이 숨겨져 있습니다!")
        else:
            print("[OK] 아이콘이 보입니다!")
    else:
        print("[FAIL] 파일 업로드 아이콘을 찾을 수 없습니다!")
        pytest.fail("파일 업로드 아이콘을 찾을 수 없습니다.")

    # Step 4: 채팅 입력창 확인
    print("\n[Step 4] 채팅 입력창 확인")
    chat_input = page.locator("textarea[placeholder*='물어보세요']").first
    if chat_input.count() == 0:
        chat_input = page.locator("textarea").first

    if chat_input.count() > 0:
        print("[OK] 채팅 입력창 발견!")

        # 채팅 입력창 위치 확인
        chat_input_box = chat_input.bounding_box()
        if chat_input_box:
            print(f"  채팅 입력창 위치: x={chat_input_box['x']:.2f}, y={chat_input_box['y']:.2f}, width={chat_input_box['width']:.2f}, height={chat_input_box['height']:.2f}")

        # 아이콘과 채팅 입력창의 관계 확인
        if upload_icon.count() > 0 and chat_input_box and icon_box:
            # 아이콘이 채팅 입력창 왼쪽에 있는지 확인
            if icon_box['x'] < chat_input_box['x'] + 50:  # 50px 이내면 왼쪽에 있다고 간주
                print("[OK] 아이콘이 채팅 입력창 왼쪽에 위치합니다!")
            else:
                print(f"[WARN] 아이콘이 채팅 입력창에서 멀리 떨어져 있습니다. (거리: {icon_box['x'] - chat_input_box['x']:.2f}px)")
    else:
        print("[FAIL] 채팅 입력창을 찾을 수 없습니다!")
        pytest.fail("채팅 입력창을 찾을 수 없습니다.")

    # 하단 영역 상세 스크린샷
    print("\n[Step 5] 하단 영역 상세 스크린샷")
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(1)
    take_screenshot(page, "file_upload_icon_bottom_area.png", screenshot_dir)

    print("\n" + "="*60)
    print("[OK] 파일 업로드 아이콘 테스트 완료!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_sidebar_ux())

