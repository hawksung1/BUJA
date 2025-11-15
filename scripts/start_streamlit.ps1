# Windows PowerShell에서 Streamlit 앱 실행 스크립트
Set-Location F:\git_projects\BUJA

# 가상환경 활성화
if (Test-Path .venv\Scripts\Activate.ps1) {
    .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "가상환경을 찾을 수 없습니다."
    Write-Host "uv sync를 실행하여 가상환경을 생성하세요."
    pause
    exit 1
}

# Streamlit 실행 (브라우저 자동 열기 방지, 자동 재기동 활성화)
python -m streamlit run app.py --server.address localhost --server.port 8501 --server.headless true

