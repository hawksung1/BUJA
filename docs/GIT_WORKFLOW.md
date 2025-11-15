# BUJA 프로젝트 Git 워크플로우

## 브랜치 전략

### 주요 브랜치

- **main**: 프로덕션 배포용 브랜치
  - 항상 안정적인 상태 유지
  - 직접 커밋 불가 (PR을 통해서만)
  - develop 브랜치에서만 merge 가능

- **develop**: 개발 브랜치
  - 모든 개발 작업의 통합 브랜치
  - 기능 브랜치에서 merge
  - 테스트 및 검증 완료 후 main으로 merge

### 보조 브랜치

- **feature/**: 기능 개발 브랜치
  - 예: `feature/user-authentication`, `feature/portfolio-analysis`
  - develop에서 분기하여 develop으로 merge

- **bugfix/**: 버그 수정 브랜치
  - 예: `bugfix/login-error`, `bugfix/calculation-bug`
  - develop 또는 main에서 분기

- **hotfix/**: 긴급 수정 브랜치
  - 예: `hotfix/security-patch`, `hotfix/critical-bug`
  - main에서 분기하여 main과 develop 모두에 merge

- **release/**: 릴리스 준비 브랜치
  - 예: `release/v1.0.0`
  - develop에서 분기하여 main으로 merge

## 워크플로우

### 1. 기능 개발 워크플로우

```bash
# 1. develop 브랜치에서 시작
git checkout develop
git pull origin develop

# 2. 기능 브랜치 생성
git checkout -b feature/your-feature-name

# 3. 개발 및 커밋
git add .
git commit -m "feat: 기능 설명"

# 4. develop에 push
git push origin feature/your-feature-name

# 5. GitHub에서 PR 생성 (feature -> develop)
# 6. 코드 리뷰 및 CI 체크 통과 후 merge
# 7. develop 브랜치에서 feature 브랜치 삭제
```

### 2. 배포 워크플로우

```bash
# 1. develop 브랜치 최신화
git checkout develop
git pull origin develop

# 2. 모든 테스트 통과 확인
uv run test

# 3. main으로 PR 생성 (develop -> main)
# 4. CI/CD 파이프라인 자동 실행:
#    - 테스트 실행
#    - 린팅 및 타입 체크
#    - 포맷팅 검사
# 5. 모든 체크 통과 후 merge
# 6. 자동으로 배포 프로세스 시작
```

### 3. 긴급 수정 워크플로우 (Hotfix)

```bash
# 1. main 브랜치에서 hotfix 브랜치 생성
git checkout main
git pull origin main
git checkout -b hotfix/urgent-fix

# 2. 수정 및 커밋
git add .
git commit -m "fix: 긴급 수정 내용"

# 3. main과 develop 모두에 merge
#    - 먼저 main에 PR 생성 및 merge
#    - 그 다음 develop에 PR 생성 및 merge
```

## 커밋 메시지 규칙

### 커밋 타입

- `feat`: 새로운 기능 추가
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 포맷팅, 세미콜론 누락 등
- `refactor`: 코드 리팩토링
- `test`: 테스트 코드 추가/수정
- `chore`: 빌드 업무 수정, 패키지 매니저 설정 등
- `perf`: 성능 개선
- `ci`: CI 설정 파일 수정

### 커밋 메시지 형식

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 예시

```
feat(auth): 사용자 인증 기능 추가

- 로그인/로그아웃 기능 구현
- JWT 토큰 기반 인증
- 비밀번호 해싱 (bcrypt)

Closes #123
```

## PR (Pull Request) 규칙

### PR 제목 형식

```
<type>: <간단한 설명>
```

### PR 템플릿

```markdown
## 변경 사항
- 

## 관련 이슈
- 

## 체크리스트
- [ ] 코드 리뷰 완료
- [ ] 테스트 통과
- [ ] 문서 업데이트 (필요시)
- [ ] 린팅 및 타입 체크 통과
```

## CI/CD 파이프라인

### 자동 실행 시점

1. **모든 Push**: develop, main 브랜치에 push 시
2. **PR 생성/업데이트**: PR이 생성되거나 업데이트될 때
3. **main 브랜치 merge**: 자동 배포 트리거

### 실행 작업

1. **Linting**: `ruff check`
2. **Type Checking**: `mypy`
3. **Format Check**: `black --check`
4. **Tests**: `pytest`
5. **Coverage**: 테스트 커버리지 리포트 생성

### 배포

- main 브랜치에 merge되면 자동으로 배포 프로세스 시작
- Docker 이미지 빌드 및 배포 (향후 구현)

## 브랜치 보호 규칙

### main 브랜치

- ✅ PR 필수
- ✅ 최소 1명의 승인 필요
- ✅ CI 체크 통과 필수
- ✅ 최신 develop과 충돌 없어야 함
- ❌ 직접 push 불가

### develop 브랜치

- ✅ PR 권장 (작은 수정은 직접 push 가능)
- ✅ CI 체크 통과 필수
- ✅ 최신 main과 충돌 없어야 함

## 브랜치 네이밍 규칙

- `feature/`: `feature/user-dashboard`
- `bugfix/`: `bugfix/login-error`
- `hotfix/`: `hotfix/security-patch`
- `release/`: `release/v1.0.0`
- `docs/`: `docs/api-documentation`

## 유용한 Git 명령어

```bash
# 브랜치 목록 확인
git branch -a

# 원격 브랜치와 동기화
git fetch origin
git pull origin develop

# 브랜치 삭제
git branch -d feature/old-feature
git push origin --delete feature/old-feature

# 현재 브랜치 확인
git branch --show-current

# 변경사항 확인
git status
git diff

# 커밋 히스토리
git log --oneline --graph --all
```

## 문제 해결

### 충돌 해결

```bash
# 1. 최신 develop 가져오기
git checkout develop
git pull origin develop

# 2. feature 브랜치로 돌아가서 merge
git checkout feature/your-feature
git merge develop

# 3. 충돌 해결 후
git add .
git commit -m "merge: develop 충돌 해결"
```

### 실수로 main에 직접 커밋한 경우

```bash
# 1. 커밋을 되돌리기
git reset HEAD~1

# 2. develop 브랜치로 이동
git checkout develop

# 3. 변경사항 적용
git cherry-pick <commit-hash>
```

---

**문서 버전**: 1.0  
**최종 업데이트**: 2024

