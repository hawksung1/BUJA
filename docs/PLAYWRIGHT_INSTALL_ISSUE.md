# Playwright 설치 무한 로딩 문제 해결

## 문제 원인

`npx playwright install chrome` 명령어가 무한 로딩되는 원인:

1. **sudo 권한 필요**: Playwright가 시스템 Chrome을 설치하려고 할 때 `sudo` 권한이 필요한데, 비대화형 환경에서 비밀번호 입력을 기다리며 멈춤
2. **잘못된 브라우저 타입**: MCP 서버가 `chrome`을 찾고 있지만, Playwright는 `chromium`을 사용해야 함
3. **브라우저 경로 미지정**: MCP 서버가 브라우저 설치 경로를 찾지 못함

## 해결 방법

### 1. MCP 서버 설정 수정 완료

`.cursor/mcp-servers.json`에 다음 설정 추가:

```json
"playwright": {
  "command": "wsl",
  "args": [
    "bash",
    "/home/user/wsl-npx.sh",
    "-y",
    "@playwright/mcp@latest",
    "--browser",
    "chromium"
  ],
  "env": {
    "PLAYWRIGHT_BROWSERS_PATH": "/home/user/.cache/ms-playwright"
  }
}
```

**변경 사항**:
- `--browser chromium` 옵션 추가: 시스템 Chrome 대신 Playwright의 Chromium 사용
- `PLAYWRIGHT_BROWSERS_PATH` 환경 변수 추가: 브라우저 설치 경로 명시

### 2. 브라우저 설치 (sudo 없이)

Playwright의 Chromium은 사용자 디렉토리에 설치되므로 sudo가 필요 없습니다:

```bash
# WSL에서
cd /mnt/f/git_projects/BUJA
export NVM_DIR=$HOME/.nvm
source $NVM_DIR/nvm.sh

# Playwright Chromium 설치 (sudo 불필요)
npx playwright install chromium
```

또는 Python Playwright 사용:

```bash
# uv 환경에서
uv run playwright install chromium
```

### 3. 멈춘 프로세스 종료

```bash
# WSL에서
echo 'user' | sudo -S pkill -9 -f playwright
echo 'user' | sudo -S pkill -9 -f reinstall_chrome
```

### 4. Cursor 재시작

설정 변경 후:
1. **Cursor 완전히 종료**
2. **Cursor 재시작**
3. MCP 서버가 새 설정으로 시작됨

## 확인 방법

### MCP 서버 연결 확인

Cursor 재시작 후 Playwright MCP 도구 사용:

```python
# 브라우저 스냅샷 시도
mcp_playwright_browser_snapshot()
```

### 브라우저 설치 확인

```bash
# WSL에서
ls -la ~/.cache/ms-playwright/chromium-*/chrome-linux/chrome
```

## 추가 참고사항

### Playwright 브라우저 타입

- ✅ `chromium`: Playwright가 관리하는 Chromium (권장, sudo 불필요)
- ❌ `chrome`: 시스템 Chrome (sudo 필요, 비권장)
- ✅ `firefox`: Firefox 브라우저
- ✅ `webkit`: WebKit 브라우저

### 브라우저 설치 경로

기본 경로: `~/.cache/ms-playwright/`

- Chromium: `~/.cache/ms-playwright/chromium-{version}/chrome-linux/chrome`
- Firefox: `~/.cache/ms-playwright/firefox-{version}/firefox/firefox`
- WebKit: `~/.cache/ms-playwright/webkit-{version}/`

## 문제가 지속될 경우

1. **캐시 삭제 후 재설치**:
   ```bash
   rm -rf ~/.cache/ms-playwright
   npx playwright install chromium
   ```

2. **MCP 서버 로그 확인**:
   - Cursor의 MCP 서버 로그 확인
   - 에러 메시지 확인

3. **수동 브라우저 경로 지정**:
   ```json
   "env": {
     "PLAYWRIGHT_BROWSERS_PATH": "/home/user/.cache/ms-playwright",
     "PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH": "/home/user/.cache/ms-playwright/chromium-1194/chrome-linux/chrome"
   }
   ```

