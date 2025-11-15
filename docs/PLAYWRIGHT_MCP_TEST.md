# Playwright MCP 연결 테스트 가이드

## 현재 상태

Playwright MCP 서버가 "Not connected" 상태입니다. 이는 다음 중 하나일 수 있습니다:

1. **Cursor가 재시작되지 않음**: MCP 서버 설정 변경 후 Cursor를 재시작해야 합니다.
2. **MCP 서버 시작 실패**: 서버가 시작되지 않았거나 에러가 발생했을 수 있습니다.
3. **브라우저 경로 문제**: 브라우저를 찾지 못할 수 있습니다.

## 해결 방법

### 1. Cursor 재시작 (필수)

MCP 서버 설정 변경 후:
1. **Cursor 완전히 종료** (모든 창 닫기)
2. **Cursor 재시작**
3. MCP 서버가 자동으로 새 설정으로 시작됨

### 2. MCP 서버 수동 확인

WSL 터미널에서:

```bash
# MCP 서버 프로세스 확인
ps aux | grep mcp-server-playwright | grep -v grep

# MCP 서버 직접 실행 테스트
cd /mnt/f/git_projects/BUJA
bash /home/user/wsl-npx.sh -y @playwright/mcp@latest --help
```

### 3. 브라우저 설치 확인

```bash
# WSL에서
ls -la ~/.cache/ms-playwright/chromium-*/chrome-linux/chrome
```

### 4. 테스트 실행

```bash
# WSL에서
cd /mnt/f/git_projects/BUJA
~/.local/bin/uv run pytest tests/e2e/test_playwright_mcp_connection.py -v
```

## MCP 서버 설정 확인

`.cursor/mcp-servers.json` 파일이 다음 설정을 포함해야 합니다:

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

## 연결 테스트

Cursor 재시작 후 다음을 시도:

1. **브라우저 스냅샷**:
   ```python
   mcp_playwright_browser_snapshot()
   ```

2. **브라우저 네비게이션**:
   ```python
   mcp_playwright_browser_navigate(url="http://localhost:8501")
   ```

3. **스크린샷 촬영**:
   ```python
   mcp_playwright_browser_take_screenshot(filename="test.png")
   ```

## 문제 해결

### "Not connected" 에러

- Cursor 재시작 확인
- MCP 서버 프로세스 실행 확인
- Cursor의 MCP 서버 로그 확인

### "Chromium distribution not found" 에러

```bash
# WSL에서
npx playwright install chromium
```

### "Permission denied" 에러

```bash
# WSL에서
chmod +x /home/user/wsl-npx.sh
```

## 다음 단계

1. ✅ MCP 서버 설정 수정 완료
2. ✅ 브라우저 설치 확인 완료
3. ⏳ **Cursor 재시작 필요**
4. ⏳ MCP 연결 테스트
5. ⏳ UI 테스트 실행

