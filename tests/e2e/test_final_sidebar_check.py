"""
최종 사이드바 확인 및 로그인 테스트
"""
import asyncio
from playwright.async_api import async_playwright
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


async def test_final():
    """최종 사이드바 및 로그인 테스트"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        try:
            print("=" * 80)
            print("최종 사이드바 UX 확인")
            print("=" * 80)
            
            # 1. 비로그인 상태 확인
            print("\n[1] 비로그인 상태 확인")
            await page.goto("http://localhost:8501/login", wait_until="networkidle")
            await page.wait_for_timeout(3000)
            
            sidebar = page.locator('[data-testid="stSidebar"]')
            if await sidebar.count() > 0:
                sidebar_text = await sidebar.inner_text()
                
                # 아이콘 중복 확인
                login_links = await page.locator('[data-testid="stSidebar"] a:has-text("Login")').all()
                print(f"Login 링크 개수: {len(login_links)}")
                
                # 아이콘 개수 확인
                icons = await page.locator('[data-testid="stSidebar"] [data-testid="stIconMaterial"]').all()
                print(f"아이콘 개수: {len(icons)}")
                
                # 기본 네비게이션 확인
                nav_menu = page.locator('[data-testid="stSidebarNav"]')
                nav_visible = await nav_menu.is_visible() if await nav_menu.count() > 0 else False
                print(f"기본 네비게이션 표시 여부: {nav_visible}")
                
                await page.screenshot(path="test_final_unauthenticated.png", full_page=True)
                print("✓ 스크린샷 저장: test_final_unauthenticated.png")
            
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
                
                # 응답 대기
                await page.wait_for_timeout(5000)
                
                # 에러 메시지 확인
                errors = await page.locator('.stAlert, .stError, [data-baseweb="notification"]').all()
                if errors:
                    print("\n에러 메시지:")
                    for err in errors:
                        text = await err.inner_text()
                        if text.strip():
                            print(f"  - {text[:200]}")
                
                # URL 확인
                current_url = page.url
                print(f"\n현재 URL: {current_url}")
                
                if "login" not in current_url.lower():
                    print("✓ 로그인 성공! 다른 페이지로 이동했습니다.")
                    
                    # 로그인 후 사이드바 확인
                    await page.wait_for_timeout(3000)
                    sidebar_after = page.locator('[data-testid="stSidebar"]')
                    if await sidebar_after.count() > 0:
                        sidebar_text_after = await sidebar_after.inner_text()
                        print("\n로그인 후 사이드바 내용:")
                        print("-" * 80)
                        print(sidebar_text_after[:1000])
                        print("-" * 80)
                        
                        # 사용자 이메일 확인
                        if "admin" in sidebar_text_after.lower():
                            print("✓ 사용자 이메일 표시됨")
                        
                        # 온보딩 상태 확인
                        if "온보딩" in sidebar_text_after:
                            print("✓ 온보딩 메뉴 표시됨")
                        
                        # 메인 메뉴 확인
                        if "Agent Chat" in sidebar_text_after or "agent chat" in sidebar_text_after.lower():
                            print("✓ Agent Chat 메뉴 표시됨")
                        
                        if "Dashboard" in sidebar_text_after or "dashboard" in sidebar_text_after.lower():
                            print("✓ Dashboard 메뉴 표시됨")
                        
                        await page.screenshot(path="test_final_authenticated.png", full_page=True)
                        print("\n✓ 스크린샷 저장: test_final_authenticated.png")
                else:
                    print("⚠ 로그인 실패 또는 페이지 이동 실패")
                    await page.screenshot(path="test_final_login_failed.png", full_page=True)
                    print("✓ 스크린샷 저장: test_final_login_failed.png")
            
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

