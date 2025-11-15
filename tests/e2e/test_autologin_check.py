"""
Autologin 기능 확인 테스트
"""
import asyncio
from playwright.async_api import async_playwright
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


async def test_autologin():
    """Autologin이 제대로 작동하는지 확인"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        try:
            print("=" * 80)
            print("Autologin 기능 확인 테스트")
            print("=" * 80)
            
            # 1. 메인 페이지 접속
            print("\n[1] 메인 페이지 접속 (app.py)")
            await page.goto("http://localhost:8501", wait_until="networkidle")
            await page.wait_for_timeout(3000)
            
            current_url = page.url
            print(f"현재 URL: {current_url}")
            
            # 로그인 페이지로 리다이렉트되었는지 확인
            if "login" in current_url.lower():
                print("⚠ 메인 페이지에서 로그인 페이지로 리다이렉트됨 (autologin이 작동하지 않음)")
            elif "agent_chat" in current_url.lower() or "onboarding" in current_url.lower():
                print("✓ Autologin 성공! Agent Chat 또는 Onboarding 페이지로 이동")
                
                # 사이드바 확인
                sidebar = page.locator('[data-testid="stSidebar"]')
                if await sidebar.count() > 0:
                    sidebar_text = await sidebar.inner_text()
                    if "admin" in sidebar_text.lower():
                        print("✓ 사용자 이메일(admin)이 사이드바에 표시됨")
                    else:
                        print("✗ 사용자 이메일이 사이드바에 표시되지 않음")
            else:
                print(f"⚠ 예상치 못한 페이지: {current_url}")
            
            await page.screenshot(path="test_autologin_main.png", full_page=True)
            print("✓ 스크린샷 저장: test_autologin_main.png")
            
            # 2. 로그인 페이지 직접 접속
            print("\n[2] 로그인 페이지 직접 접속")
            await page.goto("http://localhost:8501/login", wait_until="networkidle")
            await page.wait_for_timeout(3000)
            
            current_url_after = page.url
            print(f"로그인 페이지 접속 후 URL: {current_url_after}")
            
            if "login" not in current_url_after.lower():
                print("✓ 로그인 페이지에서 autologin으로 자동 리다이렉트됨")
            else:
                print("⚠ 로그인 페이지에 머물러 있음 (autologin이 작동하지 않음)")
            
            await page.screenshot(path="test_autologin_login_page.png", full_page=True)
            print("✓ 스크린샷 저장: test_autologin_login_page.png")
            
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
    asyncio.run(test_autologin())

