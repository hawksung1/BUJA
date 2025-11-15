#!/bin/bash
# Playwright UI 테스트 실행 스크립트
# 브라우저가 보이도록 headless=False로 실행

set -e

cd /mnt/f/git_projects/BUJA

echo "=== Streamlit 앱 시작 ==="
# Streamlit 앱을 백그라운드로 실행
~/.local/bin/uv run streamlit run app.py --server.address localhost --server.port 8501 > /tmp/streamlit.log 2>&1 &
STREAMLIT_PID=$!
echo "Streamlit PID: $STREAMLIT_PID"

# Streamlit 앱이 시작될 때까지 대기
echo "=== Streamlit 앱 시작 대기 중... ==="
for i in {1..30}; do
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        echo "✅ Streamlit 앱 시작됨!"
        break
    fi
    sleep 1
done

echo "=== Playwright UI 테스트 실행 ==="
echo "브라우저가 열립니다. 확인하세요!"
~/.local/bin/uv run python -m pytest tests/e2e/test_playwright_python.py -v --no-cov -s

echo "=== Streamlit 앱 종료 ==="
kill $STREAMLIT_PID 2>/dev/null || true

