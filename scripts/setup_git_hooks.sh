#!/bin/bash
# Git hooks 설치 스크립트

set -e

echo "🔧 Git hooks 설정 중..."

# 프로젝트 루트로 이동
cd "$(dirname "$0")/.."

# hooks 디렉토리 확인
HOOKS_DIR=".git/hooks"

if [ ! -d "$HOOKS_DIR" ]; then
    echo "❌ .git/hooks 디렉토리를 찾을 수 없습니다."
    exit 1
fi

# pre-commit hook 설치
if [ -f "$HOOKS_DIR/pre-commit" ]; then
    chmod +x "$HOOKS_DIR/pre-commit"
    echo "✅ pre-commit hook 활성화됨"
else
    echo "⚠️  pre-commit hook 파일이 없습니다."
fi

# pre-push hook 설치
if [ -f "$HOOKS_DIR/pre-push" ]; then
    chmod +x "$HOOKS_DIR/pre-push"
    echo "✅ pre-push hook 활성화됨"
else
    echo "⚠️  pre-push hook 파일이 없습니다."
fi

# pre-commit 프레임워크 설치 (선택적)
if command -v pre-commit &> /dev/null; then
    echo "📦 pre-commit 프레임워크 설치 중..."
    pre-commit install
    echo "✅ pre-commit 프레임워크 설치 완료"
else
    echo "⚠️  pre-commit이 설치되지 않았습니다."
    echo "💡 설치: uv sync --extra dev"
fi

echo "✅ Git hooks 설정 완료!"
echo ""
echo "📋 설정된 hooks:"
echo "  - pre-commit: 커밋 전 단위 테스트 실행"
echo "  - pre-push: 푸시 전 전체 테스트 실행"
echo ""
echo "💡 hooks를 스킵하려면:"
echo "  - 커밋: git commit --no-verify"
echo "  - 푸시: git push --no-verify"

