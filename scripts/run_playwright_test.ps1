# Playwright E2E 테스트 실행 스크립트
# Streamlit 앱을 시작하고 테스트를 실행합니다

Write-Host "========================================"
Write-Host "Playwright E2E 테스트 실행"
Write-Host "========================================"

$ErrorActionPreference = "Stop"

# 1. Streamlit 앱 시작
Write-Host "`n[1/3] Streamlit 앱 시작 중..."
$streamlitJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    if (Test-Path .venv\Scripts\python.exe) {
        .\.venv\Scripts\python.exe -m streamlit run app.py --server.address localhost --server.port 8501
    } else {
        Write-Host "Python not found"
    }
}

# 2. Streamlit 앱이 시작될 때까지 대기
Write-Host "[2/3] Streamlit 앱 시작 대기 중..."
$maxWait = 30
$waited = 0
$appReady = $false

while ($waited -lt $maxWait) {
    try {
        $response = Invoke-WebRequest -Uri http://localhost:8501 -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "[OK] Streamlit 앱이 실행 중입니다!"
            $appReady = $true
            break
        }
    } catch {
        # 계속 대기
    }
    Start-Sleep -Seconds 2
    $waited += 2
    Write-Host "  대기 중... ($waited/$maxWait 초)"
}

if (-not $appReady) {
    Write-Host "[ERROR] Streamlit 앱이 시작되지 않았습니다."
    Stop-Job $streamlitJob -ErrorAction SilentlyContinue
    Remove-Job $streamlitJob -ErrorAction SilentlyContinue
    exit 1
}

# 3. Playwright 테스트 실행
Write-Host "`n[3/3] Playwright 테스트 실행 중..."
$uvPath = "$env:USERPROFILE\.local\bin\uv.exe"

if (Test-Path $uvPath) {
    & $uvPath run --no-project python -m pytest tests/e2e/test_streamlit_full_flow.py::test_login_with_admin_credentials -v -s --no-cov --tb=short
    $testExitCode = $LASTEXITCODE
} else {
    Write-Host "[ERROR] uv.exe를 찾을 수 없습니다: $uvPath"
    $testExitCode = 1
}

# 4. Streamlit 앱 종료
Write-Host "`n[정리] Streamlit 앱 종료 중..."
Stop-Job $streamlitJob -ErrorAction SilentlyContinue
Remove-Job $streamlitJob -ErrorAction SilentlyContinue

# 5. 결과 출력
Write-Host "`n========================================"
if ($testExitCode -eq 0) {
    Write-Host "테스트 성공!"
} else {
    Write-Host "테스트 실패 (Exit Code: $testExitCode)"
}
Write-Host "========================================"

exit $testExitCode

