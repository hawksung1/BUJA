"""
로그인 상세 테스트
"""
import asyncio
from playwright.async_api import async_playwright
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


async def test_login():
    """로그인 프로세스를 상세히 테스트합니다."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        try:
            await page.goto("http://localhost:8501/login", wait_until="networkidle")
            await page.wait_for_timeout(3000)
            
            # 로그인 폼 찾기
            print("로그인 폼 요소 찾기...")
            email_input = page.locator('input[placeholder*="email" i]').first
            password_input = page.locator('input[type="password"]').first
            
            if await email_input.count() > 0 and await password_input.count() > 0:
                print("✓ 입력 필드를 찾았습니다.")
                
                # 값 입력
                await email_input.fill("admin")
                await password_input.fill("admin")
                print("✓ 이메일과 비밀번호를 입력했습니다.")
                
                # 로그인 버튼 찾기 및 클릭
                login_button = page.locator('button[type="submit"]:has-text("Login"), button:has-text("로그인")').first
                if await login_button.count() > 0:
                    print("✓ 로그인 버튼을 찾았습니다.")
                    await login_button.click()
                    print("✓ 로그인 버튼을 클릭했습니다.")
                else:
                    # form 내부의 submit 버튼 찾기
                    form = page.locator('form').first
                    if await form.count() > 0:
                        submit_btn = form.locator('button[type="submit"]').first
                        if await submit_btn.count() > 0:
                            await submit_btn.click()
                            print("✓ 폼 내부 submit 버튼을 클릭했습니다.")
                        else:
                            await email_input.press("Enter")
                            print("✓ Enter 키로 제출했습니다.")
                
                # 응답 대기
                print("\n응답 대기 중...")
                await page.wait_for_timeout(5000)
                
                # URL 확인
                current_url = page.url
                print(f"\n현재 URL: {current_url}")
                
                # 에러 메시지 확인
                error_messages = await page.locator('div[data-baseweb="notification"], .stAlert, .stError').all()
                if error_messages:
                    print("\n에러 메시지 발견:")
                    for i, msg in enumerate(error_messages):
                        text = await msg.inner_text()
                        print(f"  {i+1}. {text[:200]}")
                
                # 성공 메시지 확인
                success_messages = await page.locator('.stSuccess, .stInfo').all()
                if success_messages:
                    print("\n성공/정보 메시지 발견:")
                    for i, msg in enumerate(success_messages):
                        text = await msg.inner_text()
                        print(f"  {i+1}. {text[:200]}")
                
                # 페이지 내용 확인
                body_text = await page.locator('body').inner_text()
                if "agent chat" in body_text.lower() or "onboarding" in body_text.lower():
                    print("\n✓ 로그인 성공! 다른 페이지로 이동했습니다.")
                    
                    # 사이드바 확인
                    await page.wait_for_timeout(2000)
                    sidebar = page.locator('[data-testid="stSidebar"]')
                    if await sidebar.count() > 0:
                        sidebar_text = await sidebar.inner_text()
                        print("\n로그인 후 사이드바 내용:")
                        print("-" * 80)
                        print(sidebar_text)
                        print("-" * 80)
                        
                        await page.screenshot(path="test_login_success.png", full_page=True)
                        print("\n✓ 스크린샷 저장: test_login_success.png")
                else:
                    print("\n⚠ 로그인 페이지에 머물러 있습니다.")
                    await page.screenshot(path="test_login_failed.png", full_page=True)
                    print("✓ 스크린샷 저장: test_login_failed.png")
            else:
                print("✗ 로그인 폼을 찾을 수 없습니다.")
                
        except Exception as e:
            print(f"\n✗ 오류 발생: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(test_login())

