"""
DOM 구조 확인 스크립트
"""
import asyncio
import io
import sys

from playwright.async_api import async_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


async def check_dom():
    """사이드바 DOM 구조를 확인합니다."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        try:
            await page.goto("http://localhost:8501/login", wait_until="networkidle")
            await page.wait_for_timeout(3000)

            # 사이드바 전체 HTML 확인
            sidebar = page.locator('[data-testid="stSidebar"]')
            if await sidebar.count() > 0:
                sidebar_html = await sidebar.inner_html()
                print("=" * 80)
                print("사이드바 HTML 구조:")
                print("=" * 80)
                print(sidebar_html[:2000])
                print("=" * 80)

                # 네비게이션 요소 찾기
                nav_elements = await page.locator('nav, [data-testid*="Nav"], [data-testid*="nav"]').all()
                print(f"\n네비게이션 요소 개수: {len(nav_elements)}")
                for i, elem in enumerate(nav_elements):
                    testid = await elem.get_attribute("data-testid")
                    tag = await elem.evaluate("el => el.tagName")
                    print(f"  {i+1}. {tag} - data-testid: {testid}")

                # 모든 링크 확인
                links = await page.locator('[data-testid="stSidebar"] a, [data-testid="stSidebar"] button').all()
                print(f"\n사이드바 내 링크/버튼 개수: {len(links)}")
                for i, link in enumerate(links):
                    text = await link.inner_text()
                    href = await link.get_attribute("href")
                    print(f"  {i+1}. {text[:50]} - href: {href}")

            await page.screenshot(path="test_dom_check.png", full_page=True)
            print("\n✓ 스크린샷 저장: test_dom_check.png")

        except Exception as e:
            print(f"오류: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(check_dom())

