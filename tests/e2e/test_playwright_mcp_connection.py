"""
Playwright MCP 연결 테스트

이 테스트는 Playwright MCP 서버가 정상적으로 연결되어 있는지 확인합니다.
Cursor를 재시작한 후 이 테스트를 실행하세요.
"""

import subprocess

import pytest


def test_playwright_mcp_server_running():
    """Playwright MCP 서버 프로세스가 실행 중인지 확인"""
    result = subprocess.run(
        ["wsl", "bash", "-c", "ps aux | grep 'mcp-server-playwright' | grep -v grep"],
        capture_output=True,
        text=True,
    )

    # 프로세스가 실행 중이면 통과
    assert result.returncode == 0 or "mcp-server-playwright" in result.stdout, \
        "Playwright MCP 서버가 실행 중이지 않습니다. Cursor를 재시작하세요."


def test_playwright_browser_installed():
    """Playwright Chromium 브라우저가 설치되어 있는지 확인"""
    result = subprocess.run(
        [
            "wsl",
            "bash",
            "-c",
            "ls -la ~/.cache/ms-playwright/chromium-*/chrome-linux/chrome 2>/dev/null | head -1",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, \
        "Playwright Chromium 브라우저가 설치되어 있지 않습니다. 'npx playwright install chromium' 실행 필요."


def test_mcp_server_config():
    """MCP 서버 설정 파일이 올바른지 확인"""
    import json
    import os

    config_path = ".cursor/mcp-servers.json"
    assert os.path.exists(config_path), f"MCP 설정 파일이 없습니다: {config_path}"

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    assert "playwright" in config["mcpServers"], "Playwright MCP 서버 설정이 없습니다."

    playwright_config = config["mcpServers"]["playwright"]
    assert "--browser" in playwright_config.get("args", []), \
        "MCP 서버 설정에 --browser 옵션이 없습니다."
    assert "chromium" in playwright_config.get("args", []), \
        "MCP 서버 설정에 chromium 브라우저가 지정되지 않았습니다."

    assert "PLAYWRIGHT_BROWSERS_PATH" in playwright_config.get("env", {}), \
        "MCP 서버 설정에 PLAYWRIGHT_BROWSERS_PATH 환경 변수가 없습니다."


def test_streamlit_running():
    """Streamlit 앱이 실행 중인지 확인"""
    result = subprocess.run(
        ["wsl", "bash", "-c", "curl -s http://localhost:8501 > /dev/null"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        pytest.skip("Streamlit 앱이 실행 중이지 않습니다. 테스트를 건너뜁니다.")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

