# Git Hooks 가이드

## 개요

이 프로젝트는 Git hooks를 사용하여 커밋 및 푸시 전에 자동으로 테스트를 실행합니다.

## 설정된 Hooks

### 1. Pre-commit Hook
**위치**: `.git/hooks/pre-commit`

**실행 시점**: `git commit` 실행 전

**실행 내용**:
- 변경된 Python 파일 확인
- 단위 테스트 실행 (`tests/unit/`)
- 테스트 실패 시 커밋 취소

**특징**:
- 빠른 피드백 제공 (단위 테스트만 실행)
- 변경된 파일이 없으면 스킵

### 2. Pre-push Hook
**위치**: `.git/hooks/pre-push`

**실행 시점**: `git push` 실행 전

**실행 내용**:
- 코드 린팅 (`ruff check`)
- 타입 체크 (`mypy`)
- 전체 테스트 실행 (E2E 제외)
- 커버리지 확인 (70% 이상 목표)

**특징**:
- 더 엄격한 검증
- E2E 테스트는 제외 (시간 소요)

## 설치 방법

### WSL/Linux/Mac
```bash
cd /mnt/f/git_projects/BUJA
chmod +x scripts/setup_git_hooks.sh
./scripts/setup_git_hooks.sh
```

### Windows (PowerShell)
```powershell
cd F:\git_projects\BUJA
.\scripts\setup_git_hooks.ps1
```

### 수동 설치
```bash
# hooks에 실행 권한 부여
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/pre-push

# pre-commit 프레임워크 설치 (선택적)
uv sync --extra dev
pre-commit install
```

## 사용 방법

### 정상적인 워크플로우

1. **코드 변경**
   ```bash
   # 파일 수정
   vim src/services/user_service.py
   ```

2. **변경사항 스테이징**
   ```bash
   git add src/services/user_service.py
   ```

3. **커밋 (자동으로 테스트 실행)**
   ```bash
   git commit -m "feat: 사용자 서비스 개선"
   # → pre-commit hook이 자동으로 단위 테스트 실행
   ```

4. **푸시 (자동으로 전체 테스트 실행)**
   ```bash
   git push origin develop
   # → pre-push hook이 자동으로 전체 테스트 실행
   ```

### Hooks 스킵 (비권장)

**경고**: 테스트를 스킵하는 것은 권장되지 않습니다. 긴급한 경우에만 사용하세요.

```bash
# 커밋 시 hooks 스킵
git commit --no-verify -m "긴급 수정"

# 푸시 시 hooks 스킵
git push --no-verify
```

## 테스트 실행

### 수동 테스트 실행

```bash
# 단위 테스트만
uv run test-unit

# 통합 테스트만
uv run test-integration

# E2E 테스트만
uv run test-e2e

# 전체 테스트
uv run test-all

# 커버리지 포함
uv run test-cov
```

## 문제 해결

### Hook이 실행되지 않음

1. **실행 권한 확인**
   ```bash
   ls -la .git/hooks/pre-commit
   # -rwxr-xr-x 여야 함
   ```

2. **권한 부여**
   ```bash
   chmod +x .git/hooks/pre-commit
   chmod +x .git/hooks/pre-push
   ```

### 테스트 실패로 커밋/푸시 불가

1. **로컬에서 테스트 실행**
   ```bash
   uv run test-unit
   ```

2. **실패한 테스트 확인 및 수정**

3. **다시 커밋/푸시 시도**

### uv 명령을 찾을 수 없음

WSL 환경에서:
```bash
export PATH=$HOME/.local/bin:$PATH
```

또는 `~/.bashrc`에 추가:
```bash
echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

## CI/CD 통합

GitHub Actions에서도 동일한 테스트가 실행됩니다:
- `.github/workflows/ci.yml`: PR 및 push 시 자동 실행
- 린팅, 타입 체크, 테스트, 커버리지 확인

## 커버리지 목표

- **단위 테스트**: 80% 이상
- **전체 테스트**: 70% 이상
- **E2E 테스트**: 주요 시나리오 커버

## Best Practices

1. **작은 커밋**: 변경사항을 작게 나누어 커밋
2. **테스트 먼저**: 기능 개발 전 테스트 작성 (TDD)
3. **로컬 테스트**: 커밋 전 로컬에서 테스트 실행
4. **Hooks 활용**: 자동화된 검증 활용
5. **실패 시 수정**: 테스트 실패 시 즉시 수정

## 추가 설정

### Pre-commit 프레임워크

더 많은 검증을 원하면:
```bash
uv sync --extra dev
pre-commit install
```

이렇게 하면 `.pre-commit-config.yaml`의 모든 hook이 실행됩니다:
- 코드 포맷팅 (Black)
- 린팅 (Ruff)
- 타입 체크 (MyPy)
- 기타 검증

