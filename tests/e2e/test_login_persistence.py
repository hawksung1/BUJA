"""
로그인 상태 유지 테스트 스크립트
"""
import io
import sys
import time

from playwright.sync_api import sync_playwright

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def test_login_persistence():
    """로그인 후 새로고침해도 로그인 상태가 유지되는지 테스트"""
    print("=" * 60)
    print("로그인 상태 유지 테스트")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()

        try:
            # 1. 로그인 페이지 접속
            print("\n[1/5] 로그인 페이지 접속...")
            page.goto("http://localhost:8501/login", wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            page.screenshot(path="test_01_login_page.png", full_page=True)
            print("  [OK] 로그인 페이지 로드 완료")

            # 2. 로그인
            print("[2/5] 로그인 시도...")
            email_input = page.locator("input[type='text']").first
            password_input = page.locator("input[type='password']").first

            if email_input.count() > 0:
                email_input.fill("admin")
            if password_input.count() > 0:
                password_input.fill("admin")

            time.sleep(0.5)

            # 로그인 버튼 찾기 및 클릭
            submit_button = page.locator("button[type='submit']").first
            if submit_button.count() == 0:
                submit_button = page.locator("button:has-text('Login')").first
            if submit_button.count() == 0:
                submit_button = page.locator("button").filter(has_text=page.locator("text=/login|로그인/i")).first

            if submit_button.count() > 0:
                submit_button.click()
                print("  [OK] 로그인 버튼 클릭")
                time.sleep(5)  # 로그인 처리 대기
            else:
                print("  [FAIL] 로그인 버튼을 찾을 수 없습니다")
                return

            page.screenshot(path="test_02_after_login.png", full_page=True)

            # 3. 로그인 성공 확인
            print("[3/5] 로그인 성공 확인...")
            body_text = page.locator("body").inner_text()
            current_url = page.url

            if "agent chat" in body_text.lower() or "chat" in current_url.lower():
                print("  [OK] 로그인 성공 - Agent Chat 페이지로 이동됨")
            else:
                print(f"  [WARN] 예상과 다른 페이지: {current_url}")
                print(f"  페이지 내용 일부: {body_text[:200]}...")

            # 4. 새로고침
            print("[4/5] 페이지 새로고침...")
            page.reload(wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            page.screenshot(path="test_03_after_refresh.png", full_page=True)
            print("  [OK] 새로고침 완료")

            # 5. 로그인 상태 확인
            print("[5/5] 로그인 상태 확인...")
            body_text_after = page.locator("body").inner_text()
            url_after = page.url

            # 로그인 페이지로 리다이렉트되었는지 확인
            if "login" in url_after.lower():
                print("  [FAIL] 새로고침 후 로그인 페이지로 리다이렉트됨 - 로그인 상태가 유지되지 않음")
                print(f"  URL: {url_after}")
            elif "agent chat" in body_text_after.lower() or "chat" in url_after.lower():
                print("  [OK] 새로고침 후에도 로그인 상태 유지됨!")
            else:
                print("  [WARN] 예상과 다른 상태")
                print(f"  URL: {url_after}")
                print(f"  페이지 내용 일부: {body_text_after[:200]}...")

            # 추가: 쿠키 확인
            cookies = context.cookies()
            print(f"\n  쿠키 개수: {len(cookies)}")
            for cookie in cookies:
                print(f"    - {cookie['name']}: {cookie.get('value', '')[:50]}...")

            print("\n" + "=" * 60)
            print("테스트 완료!")
            print("=" * 60)

            # 브라우저를 5초간 열어둠
            print("\n브라우저를 5초간 열어둡니다...")
            time.sleep(5)

        except Exception as e:
            print(f"\n[ERROR] 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            page.screenshot(path="test_error.png", full_page=True)
        finally:
            browser.close()

if __name__ == "__main__":
    try:
        test_login_persistence()
    except KeyboardInterrupt:
        print("\n\n테스트가 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n테스트 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

