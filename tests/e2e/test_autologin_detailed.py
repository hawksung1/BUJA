"""
Autologin 상세 테스트 스크립트 - 세션 상태 초기화 후 테스트
"""
import sys
import time
import io
from playwright.sync_api import sync_playwright

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def test_autologin_detailed():
    """Autologin이 작동하는지 상세 테스트 (세션 초기화)"""
    print("=" * 60)
    print("Autologin 상세 테스트 (세션 초기화)")
    print("=" * 60)
    
    with sync_playwright() as p:
        # 새로운 브라우저 컨텍스트 생성 (쿠키/세션 없음)
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # 1. 로그인 페이지로 직접 접속 (세션 초기화)
            print("\n[1/5] 로그인 페이지로 직접 접속 (세션 초기화)...")
            page.goto("http://localhost:8501/login", wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            page.screenshot(path="test_autologin_01_login_page.png", full_page=True)
            
            current_url = page.url
            body_text = page.locator("body").inner_text()
            print(f"  URL: {current_url}")
            
            if "login" in current_url.lower():
                print("  [OK] 로그인 페이지에 있음")
            else:
                print(f"  [INFO] 로그인 페이지가 아님: {current_url}")
            
            # 2. 메인 페이지로 이동 (autologin 테스트)
            print("\n[2/5] 메인 페이지로 이동 (autologin 테스트)...")
            page.goto("http://localhost:8501", wait_until="domcontentloaded", timeout=30000)
            time.sleep(5)  # Streamlit 로딩 및 autologin 처리 대기
            page.screenshot(path="test_autologin_02_after_main.png", full_page=True)
            
            current_url = page.url
            body_text = page.locator("body").inner_text()
            print(f"  URL: {current_url}")
            
            # 3. 자동 로그인 확인
            print("\n[3/5] 자동 로그인 확인...")
            if "login" in current_url.lower():
                print("  [FAIL] 로그인 페이지에 있음 - Autologin이 작동하지 않음")
                print(f"  페이지 내용 일부: {body_text[:500]}...")
                
                # 에러 메시지 확인
                if "자동 로그인 실패" in body_text or "Auto login failed" in body_text:
                    print("  [ERROR] 자동 로그인 실패 메시지 발견")
                
                return False
            elif "agent" in current_url.lower() or "chat" in current_url.lower():
                print("  [OK] Agent Chat 페이지로 이동됨 - Autologin 성공!")
            else:
                print(f"  [WARN] 예상과 다른 페이지: {current_url}")
            
            # 4. 사용자 정보 확인
            print("\n[4/5] 사용자 정보 확인...")
            time.sleep(2)
            body_text = page.locator("body").inner_text()
            
            if "Administrator" in body_text or "admin" in body_text.lower():
                print("  [OK] 사용자 정보 확인됨 (Administrator)")
            else:
                print(f"  [WARN] 사용자 정보를 찾을 수 없음")
                print(f"  페이지 내용 일부: {body_text[:500]}...")
            
            # 5. 쿠키 및 세션 확인
            print("\n[5/5] 쿠키 및 세션 확인...")
            cookies = context.cookies()
            print(f"  쿠키 개수: {len(cookies)}")
            for cookie in cookies:
                print(f"    - {cookie['name']}: {cookie.get('value', '')[:50]}...")
            
            # 최종 스크린샷
            page.screenshot(path="test_autologin_03_final.png", full_page=True)
            
            print("\n" + "=" * 60)
            print("테스트 완료!")
            print("=" * 60)
            
            # 최종 결과
            if "agent" in current_url.lower() or "chat" in current_url.lower():
                print("\n✅ Autologin이 정상적으로 작동합니다!")
                return True
            else:
                print("\n❌ Autologin이 작동하지 않습니다.")
                return False
            
            # 브라우저를 5초간 열어둠
            print("\n브라우저를 5초간 열어둡니다...")
            time.sleep(5)
            
        except Exception as e:
            print(f"\n[ERROR] 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            page.screenshot(path="test_autologin_error.png", full_page=True)
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    try:
        result = test_autologin_detailed()
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n테스트가 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n테스트 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

