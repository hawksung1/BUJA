"""
로그인 페이지 UI 테스트 스크립트
Playwright를 사용하여 데이터베이스 진단 기능을 테스트합니다.
"""
import io
import os
import sys
import time

from playwright.sync_api import sync_playwright

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def test_login_page_diagnosis():
    """로그인 페이지의 데이터베이스 진단 기능 테스트"""
    print("=" * 60)
    print("로그인 페이지 데이터베이스 진단 기능 테스트")
    print("=" * 60)

    with sync_playwright() as p:
        # 브라우저 실행 (headless=False로 실제 브라우저 표시)
        print("\n[1/5] 브라우저 시작 중...")
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        try:
            # 로그인 페이지로 이동
            print("[2/5] 로그인 페이지로 이동 중...")
            page.goto("http://localhost:8501/login", wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)  # Streamlit 로드 대기

            # 스크린샷 폴더 생성
            os.makedirs("screenshots", exist_ok=True)

            # 페이지 스크린샷
            page.screenshot(path="screenshots/test_login_page_initial.png", full_page=True)
            print("  [OK] 초기 페이지 스크린샷 저장: screenshots/test_login_page_initial.png")

            # 이메일과 비밀번호 입력
            print("[3/5] 로그인 폼 입력 중...")
            email_input = page.locator("input[type='text']").first
            password_input = page.locator("input[type='password']").first

            if email_input.count() > 0:
                email_input.fill("test@example.com")
                print("  [OK] 이메일 입력 완료")

            if password_input.count() > 0:
                password_input.fill("testpassword")
                print("  [OK] 비밀번호 입력 완료")

            time.sleep(0.5)

            # 로그인 버튼 클릭
            print("[4/5] 로그인 버튼 클릭 중...")

            # 여러 방법으로 버튼 찾기
            submit_button = None

            # 방법 1: type='submit' 버튼
            submit_button = page.locator("button[type='submit']").first
            if submit_button.count() == 0:
                # 방법 2: "Login" 텍스트가 있는 버튼
                submit_button = page.locator("button:has-text('Login')").first
            if submit_button.count() == 0:
                # 방법 3: "로그인" 텍스트가 있는 버튼
                submit_button = page.locator("button:has-text('로그인')").first
            if submit_button.count() == 0:
                # 방법 4: form 내부의 모든 버튼 중 첫 번째
                submit_button = page.locator("form button").first
            if submit_button.count() == 0:
                # 방법 5: 모든 버튼 중 "Login" 포함
                all_buttons = page.locator("button")
                for i in range(all_buttons.count()):
                    btn = all_buttons.nth(i)
                    text = btn.inner_text().lower()
                    if "login" in text or "로그인" in text:
                        submit_button = btn
                        break

            if submit_button and submit_button.count() > 0:
                # 버튼이 보일 때까지 대기
                submit_button.wait_for(state="visible", timeout=5000)
                submit_button.click()
                print("  [OK] 로그인 버튼 클릭 완료")
                # Streamlit 응답 대기 (더 긴 대기)
                print("  Streamlit 응답 대기 중...")
                time.sleep(5)  # 응답 대기 시간 증가
            else:
                # Enter 키로 폼 제출 시도
                print("  [WARN] 로그인 버튼을 찾을 수 없습니다. Enter 키로 제출 시도...")
                password_input.press("Enter")
                time.sleep(3)  # 응답 대기

            # 결과 확인
            print("[5/5] 결과 확인 중...")
            page.screenshot(path="screenshots/test_login_page_after_submit.png", full_page=True)
            print("  [OK] 제출 후 페이지 스크린샷 저장: screenshots/test_login_page_after_submit.png")

            # 페이지 텍스트 확인
            body_text = page.locator("body").inner_text()

            # 데이터베이스 오류 메시지 확인 (더 넓은 검색)
            has_error = (
                "데이터베이스 연결 오류" in body_text or
                "Database is not available" in body_text or
                "Database is not available" in body_text or
                "진단 정보" in body_text or
                "asyncpg" in body_text.lower() or
                "데이터베이스가 초기화되지 않았습니다" in body_text
            )

            # 페이지에 에러나 성공 메시지가 있는지 확인
            has_any_message = (
                "error" in body_text.lower() or
                "에러" in body_text or
                "success" in body_text.lower() or
                "성공" in body_text or
                "invalid" in body_text.lower() or
                "잘못" in body_text
            )

            if has_error:
                print("\n[OK] 데이터베이스 오류 메시지가 표시되었습니다!")

                # 진단 정보 패널 확인
                expander = page.locator("text=/진단 정보/i").first
                if expander.count() > 0:
                    print("  [OK] 진단 정보 패널 발견")

                    # 패널 클릭하여 확장
                    expander.click()
                    time.sleep(1)
                    page.screenshot(path="screenshots/test_diagnosis_expanded.png", full_page=True)
                    print("  [OK] 확장된 진단 정보 스크린샷 저장: screenshots/test_diagnosis_expanded.png")

                    # 진단 정보 내용 확인
                    expanded_text = page.locator("body").inner_text()
                    checks = [
                        ("asyncpg", "asyncpg" in expanded_text.lower()),
                        ("데이터베이스 URL", "데이터베이스" in expanded_text or "database" in expanded_text.lower()),
                        ("해결 방법", "해결 방법" in expanded_text or "To fix" in expanded_text)
                    ]

                    print("\n  진단 정보 내용:")
                    for name, found in checks:
                        status = "[OK]" if found else "[FAIL]"
                        result = "표시됨" if found else "표시되지 않음"
                        print(f"    {status} {name}: {result}")
                else:
                    print("  [FAIL] 진단 정보 패널을 찾을 수 없습니다")
            else:
                print("\n[WARN] 데이터베이스 오류 메시지가 표시되지 않았습니다.")
                if has_any_message:
                    print("   다른 메시지가 표시되었습니다:")
                    # 에러나 성공 메시지 부분 추출
                    lines = body_text.split('\n')
                    for line in lines:
                        if any(keyword in line.lower() for keyword in ['error', '에러', 'success', '성공', 'invalid', '잘못', 'database', '데이터베이스']):
                            print(f"     - {line[:100]}")
                else:
                    print("   (데이터베이스가 연결되어 있거나 응답이 아직 완료되지 않았을 수 있습니다)")
                print(f"\n   페이지 내용 일부: {body_text[:300]}...")

            print("\n" + "=" * 60)
            print("테스트 완료!")
            print("=" * 60)
            print("\n스크린샷 파일:")
            print("  - screenshots/test_login_page_initial.png")
            print("  - screenshots/test_login_page_after_submit.png")
            if has_error:
                print("  - screenshots/test_diagnosis_expanded.png")

            # 브라우저를 열어둠 (5초)
            print("\n브라우저를 5초간 열어둡니다...")
            time.sleep(5)

        except Exception as e:
            print(f"\n[ERROR] 오류 발생: {e}")
            os.makedirs("screenshots", exist_ok=True)
            page.screenshot(path="screenshots/test_error.png", full_page=True)
            print("  오류 스크린샷 저장: screenshots/test_error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    try:
        test_login_page_diagnosis()
    except KeyboardInterrupt:
        print("\n\n테스트가 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n테스트 실행 중 오류: {e}")
        sys.exit(1)

