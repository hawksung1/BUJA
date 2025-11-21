"""
Autologin 테스트 스크립트
"""
import io
import sys
import time

from playwright.sync_api import sync_playwright

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def test_autologin():
    """Autologin이 작동하는지 테스트"""
    print("=" * 60)
    print("Autologin 테스트")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()

        try:
            # 1. 앱 메인 페이지 접속
            print("\n[1/4] 앱 메인 페이지 접속...")
            page.goto("http://localhost:8501", wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)  # Streamlit 로딩 대기
            import os
            os.makedirs("screenshots", exist_ok=True)
            page.screenshot(path="screenshots/test_autologin_01_main.png", full_page=True)
            print("  [OK] 메인 페이지 로드 완료")

            # 2. 현재 URL 확인
            print("[2/4] 현재 페이지 확인...")
            current_url = page.url
            body_text = page.locator("body").inner_text()
            print(f"  URL: {current_url}")

            # 3. 로그인 페이지인지 Agent Chat 페이지인지 확인
            print("[3/4] 페이지 타입 확인...")
            if "login" in current_url.lower():
                print("  [FAIL] 로그인 페이지로 리다이렉트됨 - Autologin이 작동하지 않음")
                print(f"  페이지 내용 일부: {body_text[:300]}...")

                # 로그인 페이지에서 자동 로그인 시도
                print("\n  수동 로그인 시도...")
                email_input = page.locator("input[type='text']").first
                password_input = page.locator("input[type='password']").first

                if email_input.count() > 0:
                    email_input.fill("admin")
                if password_input.count() > 0:
                    password_input.fill("admin")

                time.sleep(0.5)

                submit_button = page.locator("button[type='submit']").first
                if submit_button.count() == 0:
                    submit_button = page.locator("button:has-text('Login')").first

                if submit_button.count() > 0:
                    submit_button.click()
                    print("  [OK] 로그인 버튼 클릭")
                    time.sleep(5)
                else:
                    print("  [FAIL] 로그인 버튼을 찾을 수 없습니다")
            elif "agent" in current_url.lower() or "chat" in current_url.lower():
                print("  [OK] Agent Chat 페이지로 이동됨 - Autologin 성공!")
            else:
                print(f"  [WARN] 예상과 다른 페이지: {current_url}")
                print(f"  페이지 내용 일부: {body_text[:300]}...")

            # 4. 최종 상태 확인
            print("[4/4] 최종 상태 확인...")
            time.sleep(2)
            final_url = page.url
            final_body = page.locator("body").inner_text()
            page.screenshot(path="screenshots/test_autologin_02_final.png", full_page=True)

            if "agent" in final_url.lower() or "chat" in final_url.lower():
                print("  [OK] 최종적으로 Agent Chat 페이지에 있음")
                if "Investment Agent Chat" in final_body or "Agent Chat" in final_body:
                    print("  [OK] Agent Chat 콘텐츠 확인됨")
            else:
                print(f"  [FAIL] 최종 페이지가 Agent Chat이 아님: {final_url}")

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
            page.screenshot(path="screenshots/test_autologin_error.png", full_page=True)
        finally:
            browser.close()

if __name__ == "__main__":
    try:
        test_autologin()
    except KeyboardInterrupt:
        print("\n\n테스트가 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n테스트 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

