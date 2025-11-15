# Playwright UI 테스트 실행 스크립트
# Streamlit 앱을 자동으로 시작하고 테스트를 실행합니다

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Playwright UI 테스트 실행" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$ErrorActionPreference = "Continue"

# 1. Streamlit 앱 시작
Write-Host "`n[1/4] Streamlit 앱 시작 중..." -ForegroundColor Yellow

$streamlitJob = $null
$pythonPath = $null

# Python 경로 찾기
if (Test-Path .venv\Scripts\python.exe) {
    $pythonPath = ".\.venv\Scripts\python.exe"
    Write-Host "  가상환경 Python 사용: $pythonPath" -ForegroundColor Gray
} elseif (Test-Path "$env:USERPROFILE\.local\bin\uv.exe") {
    $pythonPath = "$env:USERPROFILE\.local\bin\uv.exe"
    Write-Host "  uv 사용: $pythonPath" -ForegroundColor Gray
} else {
    Write-Host "[ERROR] Python을 찾을 수 없습니다." -ForegroundColor Red
    exit 1
}

# Streamlit 앱 시작
$streamlitJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    $python = $using:pythonPath
    if ($python -like "*uv.exe") {
        & $python run streamlit run app.py --server.address localhost --server.port 8501
    } else {
        & $python -m streamlit run app.py --server.address localhost --server.port 8501
    }
}

# 2. Streamlit 앱이 시작될 때까지 대기
Write-Host "[2/4] Streamlit 앱 시작 대기 중..." -ForegroundColor Yellow
$maxWait = 30
$waited = 0
$appReady = $false

while ($waited -lt $maxWait) {
    try {
        $response = Invoke-WebRequest -Uri http://localhost:8501 -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "[OK] Streamlit 앱이 실행 중입니다!" -ForegroundColor Green
            $appReady = $true
            break
        }
    } catch {
        # 계속 대기
    }
    Start-Sleep -Seconds 2
    $waited += 2
    Write-Host "  대기 중... ($waited/$maxWait 초)" -ForegroundColor Gray
}

if (-not $appReady) {
    Write-Host "[ERROR] Streamlit 앱이 시작되지 않았습니다." -ForegroundColor Red
    Stop-Job $streamlitJob -ErrorAction SilentlyContinue
    Remove-Job $streamlitJob -ErrorAction SilentlyContinue
    exit 1
}

# 3. Playwright 테스트 실행
Write-Host "`n[3/4] Playwright 테스트 실행 중..." -ForegroundColor Yellow
Write-Host "  브라우저가 열립니다..." -ForegroundColor Gray

if ($pythonPath -like "*uv.exe") {
    & $pythonPath run python tests/e2e/test_login_ui.py
    $testExitCode = $LASTEXITCODE
} else {
    & $pythonPath tests/e2e/test_login_ui.py
    $testExitCode = $LASTEXITCODE
}

# 4. Streamlit 앱 종료
Write-Host "`n[4/4] Streamlit 앱 종료 중..." -ForegroundColor Yellow
Stop-Job $streamlitJob -ErrorAction SilentlyContinue
Remove-Job $streamlitJob -ErrorAction SilentlyContinue

# 5. 결과 출력
Write-Host "`n========================================" -ForegroundColor Cyan
if ($testExitCode -eq 0) {
    Write-Host "테스트 성공!" -ForegroundColor Green
} else {
    Write-Host "테스트 실패 (Exit Code: $testExitCode)" -ForegroundColor Red
}
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n스크린샷 파일 확인:" -ForegroundColor Yellow
if (Test-Path tests/e2e/screenshots/test_login_page_initial.png) {
    Write-Host "  - tests/e2e/screenshots/test_login_page_initial.png" -ForegroundColor Gray
}
if (Test-Path tests/e2e/screenshots/test_login_page_after_submit.png) {
    Write-Host "  - tests/e2e/screenshots/test_login_page_after_submit.png" -ForegroundColor Gray
}
if (Test-Path tests/e2e/screenshots/test_diagnosis_expanded.png) {
    Write-Host "  - tests/e2e/screenshots/test_diagnosis_expanded.png" -ForegroundColor Gray
}
if (Test-Path tests/e2e/screenshots/test_error.png) {
    Write-Host "  - tests/e2e/screenshots/test_error.png" -ForegroundColor Gray
}

exit $testExitCode

