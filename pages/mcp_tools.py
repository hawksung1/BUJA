"""
MCP Tools 관리 페이지
"""
import json

import streamlit as st

from config.logging import get_logger
from src.agents.tools.mcp_tool import MCPTool
from src.middleware import auth_middleware
from src.services.mcp_tool_service import MCPToolService

logger = get_logger(__name__)

st.set_page_config(
    page_title="MCP Tools - BUJA",
    page_icon="🔧",
    layout="wide"
)

# Authentication check
if not auth_middleware.is_authenticated():
    st.warning("Login required.")
    st.switch_page("pages/login.py")
    st.stop()

user = auth_middleware.get_current_user()
mcp_tool_service = MCPToolService()

# 공통 사이드바 렌더링
from src.utils.sidebar import render_sidebar

render_sidebar()

st.title("🔧 MCP Tools 관리")
st.markdown("""
MCP (Model Context Protocol) Tool을 추가하고 관리할 수 있습니다.
Tool을 추가하면 Agent Chat에서 자동으로 사용할 수 있습니다.
""")

# 현재 등록된 Tool 목록
st.subheader("등록된 MCP Tools")
user_tools = mcp_tool_service.load_user_tools(user.id)

if user_tools:
    for tool in user_tools:
        with st.expander(f"🔧 {tool.name} - {tool.description}"):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"**서버 URL:** {tool.mcp_server_url}")
                st.write(f"**엔드포인트:** {tool.mcp_endpoint}")
                if tool.api_key:
                    st.write(f"**API 키:** {'*' * 20} (설정됨)")

            with col2:
                if st.button("삭제", key=f"delete_{tool.name}", use_container_width=True):
                    try:
                        mcp_tool_service.remove_user_tool(user.id, tool.name)
                        st.success(f"Tool '{tool.name}'이(가) 삭제되었습니다.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"삭제 중 오류: {str(e)}")
else:
    st.info("등록된 MCP Tool이 없습니다. 아래에서 새 Tool을 추가하세요.")

st.markdown("---")

# 새 Tool 추가
st.subheader("새 MCP Tool 추가")

with st.form("add_mcp_tool_form"):
    tool_name = st.text_input("Tool 이름 *", placeholder="예: stock_price_lookup")
    tool_description = st.text_area("Tool 설명 *", placeholder="예: 주식 가격을 조회합니다.")

    col1, col2 = st.columns(2)
    with col1:
        mcp_server_url = st.text_input("MCP 서버 URL *", placeholder="https://api.example.com")
    with col2:
        mcp_endpoint = st.text_input("엔드포인트 경로 *", placeholder="tools/stock-price")

    api_key = st.text_input("API 키 (선택사항)", type="password", help="필요한 경우 API 키를 입력하세요.")

    st.markdown("**파라미터 스키마 (JSON Schema)**")
    st.caption("Tool 실행에 필요한 파라미터를 정의합니다. JSON Schema 형식으로 입력하세요.")

    # 기본 파라미터 스키마 예시
    default_schema = {
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string",
                "description": "주식 심볼"
            }
        },
        "required": ["symbol"]
    }

    parameters_schema_json = st.text_area(
        "파라미터 스키마 (JSON)",
        value=json.dumps(default_schema, indent=2, ensure_ascii=False),
        height=200,
        help="JSON Schema 형식으로 파라미터를 정의하세요."
    )

    submit_button = st.form_submit_button("Tool 추가", use_container_width=True)

    if submit_button:
        if not tool_name or not tool_description or not mcp_server_url or not mcp_endpoint:
            st.error("필수 항목을 모두 입력해주세요.")
        else:
            try:
                # JSON 스키마 파싱
                parameters_schema = json.loads(parameters_schema_json)

                # MCPTool 생성
                new_tool = MCPTool(
                    name=tool_name,
                    description=tool_description,
                    mcp_server_url=mcp_server_url,
                    mcp_endpoint=mcp_endpoint,
                    parameters_schema=parameters_schema,
                    api_key=api_key if api_key else None
                )

                # Tool 추가
                mcp_tool_service.add_user_tool(user.id, new_tool)
                st.success(f"Tool '{tool_name}'이(가) 추가되었습니다!")
                st.info("Agent Chat에서 이 Tool을 사용할 수 있습니다.")
                st.rerun()

            except json.JSONDecodeError as e:
                st.error(f"JSON 스키마 형식 오류: {str(e)}")
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Tool 추가 중 오류: {str(e)}")
                logger.error(f"Failed to add MCP tool: {e}", exc_info=True)

# 예시 섹션
with st.expander("📖 MCP Tool 예시"):
    st.markdown("""
    ### 예시 1: 주식 가격 조회 Tool
    
    ```json
    {
      "name": "get_stock_price",
      "description": "주식 가격을 조회합니다.",
      "mcp_server_url": "https://api.finance.example.com",
      "mcp_endpoint": "v1/stock/price",
      "parameters_schema": {
        "type": "object",
        "properties": {
          "symbol": {
            "type": "string",
            "description": "주식 심볼 (예: AAPL, TSLA)"
          }
        },
        "required": ["symbol"]
      }
    }
    ```
    
    ### 예시 2: 뉴스 검색 Tool
    
    ```json
    {
      "name": "search_news",
      "description": "투자 관련 뉴스를 검색합니다.",
      "mcp_server_url": "https://api.news.example.com",
      "mcp_endpoint": "search",
      "parameters_schema": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "검색어"
          },
          "limit": {
            "type": "integer",
            "description": "결과 개수",
            "default": 10
          }
        },
        "required": ["query"]
      }
    }
    ```
    """)

