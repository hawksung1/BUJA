# Playwright MCP 연결 문제 해결

## 문제 원인

`.cursor/mcp-servers.json`에서 잘못된 패키지 이름을 사용하고 있었습니다:
- ❌ `@modelcontextprotocol/server-playwright` (존재하지 않음)
- ✅ `@playwright/mcp@latest` (올바른 패키지)

## 해결 방법

### 1. MCP 서버 설정 수정 완료

`.cursor/mcp-servers.json` 파일이 수정되었습니다:
```json
"playwright": {
  "command": "wsl",
  "args": [
    "bash",
    "/home/user/wsl-npx.sh",
    "-y",
    "@playwright/mcp@latest"
  ]
}
```

### 2. Cursor 재시작 필요

MCP 서버 설정 변경 후:
1. **Cursor 완전히 종료**
2. **Cursor 재시작**
3. MCP 서버가 자동으로 새 설정으로 시작됨

### 3. 연결 확인

Cursor 재시작 후:
- Playwright MCP 도구가 정상 작동하는지 확인
- 브라우저 테스트 실행

## 사용 가능한 Playwright MCP 패키지

검색 결과에서 찾은 패키지들:
- `@playwright/mcp` (v0.0.47) - **권장**
- `@iflow-mcp/better-playwright-mcp` (v3.2.0)
- `@executeautomation/playwright-mcp-server` (v1.0.6)
- `playwright-mcp` (v0.0.13)

## 추가 설정 (필요시)

### 브라우저 설치

Playwright MCP가 작동하려면 브라우저가 설치되어 있어야 합니다:

```bash
# WSL에서
npx playwright install chromium
```

### 환경 변수 설정

필요한 경우 `.cursor/mcp-servers.json`에 환경 변수 추가:

```json
"playwright": {
  "command": "wsl",
  "args": [
    "bash",
    "/home/user/wsl-npx.sh",
    "-y",
    "@playwright/mcp@latest"
  ],
  "env": {
    "PLAYWRIGHT_BROWSERS_PATH": "/home/user/.cache/ms-playwright"
  }
}
```

## 테스트

Cursor 재시작 후 다음을 시도:

1. Playwright MCP 도구 사용
2. 브라우저로 localhost:8501 접속
3. UI 테스트 실행

