# BUJA 프로젝트

BUJA 프로젝트는 Streamlit 기반의 웹 애플리케이션입니다.

## 기술 스택

- **Python 3.10+**
- **Streamlit** - 웹 UI 프레임워크
- **uv** - Python 패키지 관리자
- **WSL** - 개발 환경

## 사전 요구사항

### 1. WSL 환경 설정

WSL2가 설치되어 있어야 합니다:

```bash
# WSL 버전 확인
wsl --version

# WSL2 설치 (필요시)
wsl --install
```

### 2. Python 설치

WSL 내에서 Python 3.10 이상이 필요합니다:

```bash
# Python 버전 확인
python3 --version

# Python 설치 (Ubuntu/Debian)
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### 3. uv 설치

```bash
# uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 또는 pip로 설치
pip install uv

# 설치 확인
uv --version
```

## 프로젝트 설정

### 1. 저장소 클론

```bash
cd ~/projects  # 또는 원하는 디렉토리
git clone https://github.com/hawksung1/BUJA.git
cd BUJA
```

### 2. 의존성 설치

```bash
# uv를 사용한 의존성 설치
uv sync
```

이 명령어는:
- 가상 환경 생성
- `pyproject.toml`에 정의된 모든 의존성 설치
- 프로젝트를 편집 가능 모드로 설치

### 3. 로컬 데이터베이스 설정 (Docker 사용)

로컬 개발을 위한 PostgreSQL 데이터베이스를 Docker로 실행:

**Windows (PowerShell):**
```powershell
.\scripts\setup_local_db.ps1
```

**Linux/WSL/Mac:**
```bash
chmod +x scripts/setup_local_db.sh
./scripts/setup_local_db.sh
```

또는 직접 Docker Compose로 실행:
```bash
docker-compose -f docker-compose.local.yml up -d postgres
```

데이터베이스가 실행되면 `.env.local` 파일의 설정으로 자동 연결됩니다.

**데이터베이스 중지:**
```bash
docker-compose -f docker-compose.local.yml down
```

**데이터베이스 로그 확인:**
```bash
docker-compose -f docker-compose.local.yml logs -f postgres
```

또는 `uv run` 명령어 사용:
```bash
uv run db-up      # 데이터베이스 시작
uv run db-down    # 데이터베이스 중지
uv run db-logs    # 데이터베이스 로그 확인
uv run db-reset   # 데이터베이스 초기화 (모든 데이터 삭제)
```

## 프로젝트 실행

### 개발 모드 실행

```bash
# Streamlit 앱 실행
uv run dev

# 또는 직접 실행
uv run streamlit run app.py
```

앱이 실행되면 브라우저에서 자동으로 열리거나, 터미널에 표시된 URL로 접속하세요 (기본: `http://localhost:8501`).

### 포트 지정 실행

```bash
uv run serve
# 또는
uv run streamlit run app.py --server.port 8501
```

## 프로젝트 구조

```
BUJA/
├── app.py              # Streamlit 메인 앱
├── pages/              # Streamlit 멀티 페이지
├── src/                # 소스 코드
├── data/               # 데이터 파일
├── docs/               # 프로젝트 문서
│   ├── REQUIREMENTS.md # 요구사항 명세서
│   ├── DESIGN.md       # 프로그램 설계서
│   └── WBS.md          # 작업 분해 구조
├── tests/              # 테스트 코드
├── pyproject.toml      # 프로젝트 설정 및 의존성
├── uv.lock             # 의존성 락 파일
├── .gitignore
└── README.md
```

## 프로젝트 문서

상세한 설계 및 계획 문서는 [`docs/`](./docs/) 디렉토리를 참조하세요:

- **[요구사항 명세서](./docs/REQUIREMENTS.md)** - 기능 및 비기능 요구사항
- **[프로그램 설계서](./docs/DESIGN.md)** - 시스템 아키텍처 및 기술 설계
- **[작업 분해 구조](./docs/WBS.md)** - 개발 계획 및 일정
- **[Git 워크플로우](./docs/GIT_WORKFLOW.md)** - 브랜치 전략 및 개발 프로세스

## UV 스크립트 명령어

`pyproject.toml`에 정의된 스크립트는 `uv run <스크립트명>`으로 실행할 수 있습니다:

```bash
# 개발 서버 실행
uv run dev

# 앱 실행
uv run app

# 서버 실행 (포트 지정)
uv run serve

# 의존성 설치
uv run install

# 초기 설정
uv run setup

# 테스트 실행
uv run test
```

## 개발 가이드

### 새 페이지 추가

Streamlit의 멀티 페이지 기능을 사용하려면 `pages/` 디렉토리를 생성하고 페이지 파일을 추가하세요:

```bash
mkdir -p pages
```

`pages/example.py` 파일 생성:

```python
import streamlit as st

st.title("예제 페이지")
st.write("새 페이지 내용")
```

### 의존성 추가

새로운 Python 패키지를 추가하려면:

```bash
# 패키지 추가
uv add package-name

# 개발 의존성 추가
uv add --dev package-name
```

### 가상 환경 활성화

uv가 자동으로 가상 환경을 관리하지만, 수동으로 활성화하려면:

```bash
# 가상 환경 경로 확인
uv venv

# 가상 환경 활성화
source .venv/bin/activate  # Linux/WSL
```

## WSL에서 Windows 브라우저 열기

WSL에서 Streamlit을 실행하면 기본적으로 WSL 내부 브라우저를 열려고 시도합니다. Windows 브라우저에서 열려면:

```bash
# Windows 브라우저로 자동 열기 비활성화
streamlit run app.py --server.headless true

# 또는 브라우저 설정
export BROWSER=wslview
streamlit run app.py
```

또는 터미널에 표시된 URL을 복사하여 Windows 브라우저에서 직접 열 수 있습니다.

## 문제 해결

### uv 명령어를 찾을 수 없는 경우

```bash
# uv 경로를 PATH에 추가
export PATH="$HOME/.cargo/bin:$PATH"

# 또는 ~/.bashrc 또는 ~/.zshrc에 추가
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 포트가 이미 사용 중인 경우

```bash
# 다른 포트 사용
streamlit run app.py --server.port 8502
```

### 권한 오류

```bash
# 실행 권한 부여
chmod +x app.py
```

## 라이선스

MIT License
