# Git hooks 설치 스크립트 (PowerShell)

Write-Host "🔧 Git hooks 설정 중..." -ForegroundColor Cyan

# 프로젝트 루트로 이동
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

# hooks 디렉토리 확인
$HooksDir = ".git\hooks"

if (-not (Test-Path $HooksDir)) {
    Write-Host "❌ .git\hooks 디렉토리를 찾을 수 없습니다." -ForegroundColor Red
    exit 1
}

# pre-commit hook 활성화
if (Test-Path "$HooksDir\pre-commit") {
    Write-Host "✅ pre-commit hook 활성화됨" -ForegroundColor Green
} else {
    Write-Host "⚠️  pre-commit hook 파일이 없습니다." -ForegroundColor Yellow
}

# pre-push hook 활성화
if (Test-Path "$HooksDir\pre-push") {
    Write-Host "✅ pre-push hook 활성화됨" -ForegroundColor Green
} else {
    Write-Host "⚠️  pre-push hook 파일이 없습니다." -ForegroundColor Yellow
}

# pre-commit 프레임워크 설치 (선택적)
if (Get-Command pre-commit -ErrorAction SilentlyContinue) {
    Write-Host "📦 pre-commit 프레임워크 설치 중..." -ForegroundColor Cyan
    pre-commit install
    Write-Host "✅ pre-commit 프레임워크 설치 완료" -ForegroundColor Green
} else {
    Write-Host "⚠️  pre-commit이 설치되지 않았습니다." -ForegroundColor Yellow
    Write-Host "💡 설치: uv sync --extra dev" -ForegroundColor Yellow
}

Write-Host "✅ Git hooks 설정 완료!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 설정된 hooks:" -ForegroundColor Cyan
Write-Host "  - pre-commit: 커밋 전 단위 테스트 실행"
Write-Host "  - pre-push: 푸시 전 전체 테스트 실행"
Write-Host ""
Write-Host "💡 hooks를 스킵하려면:" -ForegroundColor Yellow
Write-Host "  - 커밋: git commit --no-verify"
Write-Host "  - 푸시: git push --no-verify"

