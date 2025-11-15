# nvm-windows를 사용한 Node.js 설치 가이드

## 1단계: nvm-windows 설치

### 다운로드 및 설치

1. **GitHub 릴리스 페이지 방문**
   - https://github.com/coreybutler/nvm-windows/releases
   - 최신 릴리스의 `nvm-setup.exe` 다운로드

2. **설치 실행**
   - 다운로드한 `nvm-setup.exe` 실행
   - 설치 마법사 따라 진행
   - **중요**: 설치 후 **새 터미널**을 열어야 합니다 (환경 변수 적용)

3. **설치 확인**
   ```powershell
   nvm version
   ```

## 2단계: Node.js 설치

### 방법 1: 자동 설치 스크립트 사용 (권장)

프로젝트 루트에 있는 `install-nodejs.ps1` 스크립트를 실행:

```powershell
.\install-nodejs.ps1
```

### 방법 2: 수동 설치

```powershell
# 사용 가능한 Node.js 버전 확인
nvm list available

# 최신 LTS 버전 설치
nvm install lts

# 또는 특정 버전 설치 (예: 20.11.0)
nvm install 20.11.0

# 설치된 버전 사용
nvm use lts
# 또는
nvm use 20.11.0
```

## 3단계: 설치 확인

```powershell
node --version
npm --version
npx --version
```

모든 명령이 정상적으로 버전을 출력하면 설치 완료입니다.

## 4단계: Cursor 재시작

Node.js 설치 후 **Cursor를 완전히 종료하고 다시 시작**해야 MCP 서버가 정상 작동합니다.

## 유용한 nvm 명령어

```powershell
# 설치된 Node.js 버전 목록
nvm list

# 특정 버전 사용
nvm use <version>

# 기본 버전 설정
nvm alias default <version>

# Node.js 버전 제거
nvm uninstall <version>
```

## 문제 해결

### nvm 명령을 찾을 수 없는 경우
- 새 터미널을 열어보세요
- 시스템 재시작이 필요할 수 있습니다
- 환경 변수 PATH에 nvm 경로가 추가되었는지 확인

### 권한 오류 발생 시
- PowerShell을 **관리자 권한**으로 실행
- 또는 사용자 디렉토리에 설치하도록 설정

## 참고

- nvm-windows는 Windows 전용 Node Version Manager입니다
- Linux/Mac의 nvm과는 다른 프로젝트입니다
- 공식 저장소: https://github.com/coreybutler/nvm-windows

