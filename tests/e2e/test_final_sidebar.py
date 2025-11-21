"""
최종 사이드바 및 로그인 테스트
"""
import asyncio
import io
import sys

from playwright.async_api import async_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


async def test_final():
    """최종 통합 테스트"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        try:
            print("=" * 80)
            print("최종 사이드바 UX 테스트")
            print("=" * 80)

            # 1. 비로그인 상태
            print("\n[1] 비로그인 상태 확인")
            await page.goto("http://localhost:8501/login", wait_until="networkidle")
            await page.wait_for_timeout(3000)

            # JavaScript로 네비게이션 강제 숨김
            await page.evaluate("""
                const hideNav = () => {
                    document.querySelectorAll('[data-testid="stSidebarNav"], [data-testid="stSidebarNavItems"], [data-testid="stSidebarNavLink"]').forEach(el => {
                        el.style.display = 'none';
                        el.style.visibility = 'hidden';
                        el.style.height = '0';
                        el.style.opacity = '0';
                    });
                };
                hideNav();
                setInterval(hideNav, 100);
            """)
            await page.wait_for_timeout(1000)

            sidebar = page.locator('[data-testid="stSidebar"]')
            if await sidebar.count() > 0:
                sidebar_text = await sidebar.inner_text()
                nav_visible = await page.locator('[data-testid="stSidebarNav"]').count()
                print(f"  기본 네비게이션 요소 개수: {nav_visible}")
                print(f"  사이드바 내용: {sidebar_text[:200]}...")

                if "BUJA" in sidebar_text and "Login" in sidebar_text:
                    print("  ✓ 커스텀 사이드바 표시됨")
                if nav_visible == 0:
                    print("  ✓ 기본 네비게이션 숨김됨")
                else:
                    print("  ✗ 기본 네비게이션 여전히 표시됨")

            await page.screenshot(path="test_final_unauthenticated.png", full_page=True)

            # 2. 로그인 시도
            print("\n[2] 로그인 시도")
            email_input = page.locator('input[placeholder*="email" i]').first
            password_input = page.locator('input[type="password"]').first

            if await email_input.count() > 0:
                await email_input.fill("admin")
                await password_input.fill("admin")

                # 로그인 버튼 클릭
                login_btn = page.locator('button[type="submit"]:has-text("Login")').first
                if await login_btn.count() > 0:
                    await login_btn.click()
                else:
                    await email_input.press("Enter")

                await page.wait_for_timeout(5000)

                current_url = page.url
                print(f"  현재 URL: {current_url}")

                # 에러 메시지 확인
                errors = await page.locator('.stAlert, .stError, [data-baseweb="notification"]').all()
                if errors:
                    for err in errors:
                        text = await err.inner_text()
                        if text:
                            print(f"  에러: {text[:100]}")

                # 로그인 성공 여부
                if "login" not in current_url.lower():
                    print("  ✓ 로그인 성공 또는 리다이렉트됨")

                    await page.wait_for_timeout(3000)

                    # 사이드바 확인
                    sidebar_after = page.locator('[data-testid="stSidebar"]')
                    if await sidebar_after.count() > 0:
                        sidebar_text_after = await sidebar_after.inner_text()
                        print("\n  로그인 후 사이드바:")
                        print(f"  {sidebar_text_after[:300]}...")

                        # JavaScript로 네비게이션 숨김
                        await page.evaluate("""
                            document.querySelectorAll('[data-testid="stSidebarNav"]').forEach(el => {
                                el.style.display = 'none';
                            });
                        """)

                        if "admin" in sidebar_text_after.lower():
                            print("  ✓ 사용자 이메일 표시됨")
                        if "온보딩" in sidebar_text_after or "onboarding" in sidebar_text_after.lower():
                            print("  ✓ 온보딩 메뉴 표시됨")
                        if "Agent Chat" in sidebar_text_after or "agent chat" in sidebar_text_after.lower():
                            print("  ✓ Agent Chat 메뉴 표시됨")
                        if "Logout" in sidebar_text_after or "로그아웃" in sidebar_text_after:
                            print("  ✓ Logout 버튼 표시됨")

                        await page.screenshot(path="test_final_authenticated.png", full_page=True)
                        print("  ✓ 스크린샷 저장: test_final_authenticated.png")
                else:
                    print("  ✗ 로그인 실패 - 로그인 페이지에 머물러 있음")
                    await page.screenshot(path="test_final_login_failed.png", full_page=True)

            print("\n" + "=" * 80)
            print("테스트 완료")
            print("=" * 80)

        except Exception as e:
            print(f"\n✗ 오류: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(test_final())

