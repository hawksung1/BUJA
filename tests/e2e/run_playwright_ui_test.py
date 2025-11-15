#!/usr/bin/env python3
"""
Playwright로 직접 브라우저를 열고 UI 테스트 실행
브라우저가 실제로 열리는지 확인
"""
import sys
import time
import subprocess
import httpx
from playwright.sync_api import sync_playwright

def wait_for_streamlit(url, timeout=60):
    """Streamlit 앱이 시작될 때까지 대기"""
    print(f"⏳ Streamlit 앱 시작 대기 중... ({url})")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = httpx.get(url, timeout=2, follow_redirects=True)
            if response.status_code == 200:
                print(f"✅ Streamlit 앱 시작됨! ({time.time() - start_time:.1f}초)")
                return True
        except:
            pass
        time.sleep(1)
    
    print(f"❌ Streamlit 앱이 {timeout}초 내에 시작되지 않았습니다.")
    return False

def test_streamlit_ui():
    """Streamlit UI 테스트 - 브라우저가 실제로 열림"""
    app_url = "http://localhost:8501"
    
    print("=" * 60)
    print("Playwright UI 테스트 시작")
    print("=" * 60)
    print(f"테스트 URL: {app_url}")
    print()
    
    # Streamlit 앱이 실행 중인지 확인
    if not wait_for_streamlit(app_url):
        print("❌ Streamlit 앱을 먼저 실행해주세요:")
        print("   ~/.local/bin/uv run streamlit run app.py --server.address localhost --server.port 8501")
        return False
    
    print("브라우저가 열립니다. 확인하세요!")
    print()
    
    with sync_playwright() as p:
        # 브라우저를 headless=False로 열어서 보이도록 함
        print("✅ Chromium 브라우저 시작 중...")
        browser = p.chromium.launch(
            headless=False,  # 브라우저가 보이도록
            slow_mo=1000,   # 1초씩 천천히 실행 (관찰하기 쉽게)
        )
        
        print("✅ 새 페이지 생성 중...")
        page = browser.new_page()
        
        print(f"✅ {app_url}로 이동 중...")
        page.goto(app_url, wait_until="networkidle", timeout=30000)
        
        # 페이지 정보 출력
        title = page.title()
        print(f"✅ 페이지 로드 완료!")
        print(f"   제목: {title}")
        
        # 페이지 텍스트 확인
        body_text = page.locator("body").inner_text()
        print(f"   콘텐츠 길이: {len(body_text)} 문자")
        
        # BUJA 또는 환영 메시지 확인
        if "buja" in body_text.lower() or "환영" in body_text or "welcome" in body_text.lower():
            print("   ✅ BUJA 앱 콘텐츠 확인됨")
        else:
            print("   ⚠️  BUJA 앱 콘텐츠를 찾을 수 없음")
        
        # 스크린샷 저장
        import os
        os.makedirs("tests/e2e/screenshots", exist_ok=True)
        screenshot_path = "tests/e2e/screenshots/ui_test_result.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"   ✅ 스크린샷 저장: {screenshot_path}")
        
        # 5초간 브라우저 열어두기 (확인하기 위해)
        print()
        print("⏳ 5초간 브라우저를 열어둡니다. 확인하세요...")
        time.sleep(5)
        
        print("✅ 브라우저 닫는 중...")
        browser.close()
    
    print()
    print("=" * 60)
    print("✅ 테스트 완료!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_streamlit_ui()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

