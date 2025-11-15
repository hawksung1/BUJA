# MCP (Model Context Protocol) 설정 가이드

## Context7 MCP 추가

Context7은 최신 문서와 코드 예제를 LLM 컨텍스트에 제공하여 오래되거나 부정확한 정보를 방지하는 도구입니다.

### 설정 방법

1. **Cursor 설정 열기**
   - `Ctrl + ,` (설정 열기)
   - 또는 `File` → `Preferences` → `Settings`

2. **MCP 설정 찾기**
   - 검색창에 "MCP" 또는 "Model Context Protocol" 입력
   - `Features` → `Model Context Protocol` 섹션으로 이동

3. **모든 MCP 서버 추가** (권장)
   - 프로젝트에 준비된 설정 파일 사용: `.cursor/mcp-servers.json`
   - 이 파일의 내용을 Cursor 설정의 `mcpServers` 섹션에 복사
   - 또는 Cursor 설정 UI에서 "Add MCP Server"를 클릭하여 각 서버 추가

**빠른 설정 방법**:
1. `.cursor/mcp-servers.json` 파일 열기
2. 전체 내용 복사
3. Cursor 설정 파일(`%APPDATA%\Cursor\User\settings.json`) 열기
4. 기존 `mcpServers` 섹션이 있으면 병합, 없으면 추가
5. GitHub 토큰이 필요한 경우 `GITHUB_PERSONAL_ACCESS_TOKEN` 값 설정
6. Cursor 재시작

### Context7 사용법
- 최신 문서 확인이 필요할 때 자동으로 활용됩니다
- 프로젝트 가이드에서 "Context7 MCP 활용"으로 명시된 경우 사용

---

## 프로젝트에 추가된 MCP 툴

다음 MCP 툴들이 프로젝트에 추가되었습니다 (`.cursor/mcp-servers.json` 참조):

### 1. **Context7 MCP** ⭐ 필수
- **용도**: 최신 문서 및 코드 예제 제공
- **BUJA 프로젝트 활용**:
  - 최신 프레임워크 문서 확인
  - 정확한 코드 생성 지원
  - 오래된 정보 방지

**설정 예시**:
```json
{
  "context7": {
    "command": "npx",
    "args": [
      "-y",
      "@upstash/context7-mcp@latest"
    ]
  }
}
```

### 2. **GitHub MCP** ⭐ 추천
- **용도**: GitHub API 자동화 및 상호작용
- **BUJA 프로젝트 활용**:
  - 코드 리뷰 자동화
  - 이슈 관리
  - PR 자동화
  - 코드 검색 및 분석

**설정 예시**:
```json
{
  "github": {
    "command": "npx",
    "args": [
      "-y",
      "@modelcontextprotocol/server-github"
    ],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token_here"
    }
  }
}
```

### 3. **Playwright MCP** ⭐ 추천
- **용도**: 브라우저 자동화 및 UI 테스트
- **BUJA 프로젝트 활용**:
  - Streamlit UI 테스트 자동화
  - E2E 테스트 실행
  - UI 변경 검증 (가이드에서 필수로 명시됨)

**설정 예시**:
```json
{
  "playwright": {
    "command": "npx",
    "args": [
      "-y",
      "@modelcontextprotocol/server-playwright"
    ]
  }
}
```

### 4. **Filesystem MCP**
- **용도**: 파일 시스템 접근 및 조작
- **BUJA 프로젝트 활용**:
  - 프로젝트 파일 읽기/쓰기
  - 데이터 파일 관리
  - 로그 파일 처리

**설정 예시**:
```json
{
  "filesystem": {
    "command": "npx",
    "args": [
      "-y",
      "@modelcontextprotocol/server-filesystem",
      "/"
    ]
  }
}
```

### 5. **Brave Search MCP**
- **용도**: 웹 검색 및 정보 수집
- **BUJA 프로젝트 활용**:
  - 투자 정보 검색
  - 시장 트렌드 조사
  - 최신 뉴스 수집

**설정 예시**:
```json
{
  "brave-search": {
    "command": "npx",
    "args": [
      "-y",
      "@modelcontextprotocol/server-brave-search"
    ],
    "env": {
      "BRAVE_API_KEY": "your_brave_api_key_here"
    }
  }
}
```

---

## 설정 파일

프로젝트에 준비된 설정 파일: **`.cursor/mcp-servers.json`**

이 파일에는 다음 MCP 서버들이 포함되어 있습니다:
- ✅ **context7**: 최신 문서 및 코드 예제 제공 (`@upstash/context7-mcp@latest`)
- ✅ **github**: GitHub API 자동화 (`@modelcontextprotocol/server-github`)
- ✅ **playwright**: 브라우저 자동화 및 UI 테스트 (`@modelcontextprotocol/server-playwright`)
- ✅ **filesystem**: 파일 시스템 접근 및 조작 (`@modelcontextprotocol/server-filesystem`)
- ✅ **brave-search**: 웹 검색 및 정보 수집 (`@modelcontextprotocol/server-brave-search`)

### 설정 적용 방법

1. **Cursor 설정 파일 열기**
   - Windows: `%APPDATA%\Cursor\User\settings.json`
   - 또는 Cursor에서 `Ctrl + Shift + P` → "Preferences: Open User Settings (JSON)"

2. **설정 병합**
   - `.cursor/mcp-servers.json`의 내용을 복사
   - Cursor 설정 파일의 `mcpServers` 섹션에 추가 또는 병합
   - 기존 `mcpServers`가 있으면 새 서버들을 추가

3. **GitHub 토큰 설정** (선택사항)
   - GitHub MCP를 사용하려면 Personal Access Token 필요
   - GitHub → Settings → Developer settings → Personal access tokens → Generate new token
   - `mcpServers.github.env.GITHUB_PERSONAL_ACCESS_TOKEN`에 토큰 설정

4. **Cursor 재시작**
   - 설정 적용을 위해 Cursor 재시작

---

## 참고 사항

1. **설정 파일 위치**
   - Windows: `%APPDATA%\Cursor\User\settings.json`
   - 또는 Cursor 설정 UI에서 관리

2. **환경 변수**
   - GitHub MCP 등 일부 툴은 API 토큰이 필요할 수 있습니다
   - 환경 변수는 `.env` 파일이나 시스템 환경 변수로 관리

3. **설정 적용**
   - 설정 변경 후 Cursor 재시작 필요할 수 있습니다

4. **프로젝트 가이드**
   - `.cursor/CURSOR_GUIDE.md`에서 MCP 활용 방법 참조
   - 작업 원칙에 "Context7 MCP 활용" 명시됨

---

## 업데이트 이력

- 2024-XX-XX: 초기 설정 가이드 작성
- Context7 MCP 추가 완료
- 모든 추천 MCP 툴 추가 완료 (context7, github, playwright, filesystem, brave-search)
- `.cursor/mcp-servers.json` 설정 파일 생성
- 정확한 패키지 이름으로 수정 완료

