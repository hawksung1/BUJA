@echo off
REM Windows에서 Streamlit 앱 실행 스크립트
cd /d F:\git_projects\BUJA

REM 가상환경 활성화
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo 가상환경을 찾을 수 없습니다.
    echo uv sync를 실행하여 가상환경을 생성하세요.
    pause
    exit /b 1
)

REM Streamlit 실행 (브라우저 자동 열기 방지, 자동 재기동 활성화)
python -m streamlit run app.py --server.address localhost --server.port 8501 --server.headless true

pause

