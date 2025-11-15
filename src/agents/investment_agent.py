"""
투자 상담 Agent 구현 (Tool-based Agent)
"""
from typing import Optional, Dict, Any, List, AsyncGenerator
from src.agents.base_agent import BaseAgent
from src.agents.tools import BaseTool, PortfolioAnalysisTool, RiskCalculatorTool, RecommendationTool
from src.external.llm_client import LLMClient, get_llm_client
from config.logging import get_logger
import json

logger = get_logger(__name__)


# Investment Agent System Prompt
INVESTMENT_AGENT_SYSTEM_PROMPT = """You are a professional investment advisor. Provide personalized investment advice 
considering the user's investment preferences, financial situation, and goals. Follow these principles:

1. Respect the user's risk tolerance
2. Clearly explain the rationale behind investment decisions
3. Explicitly state risks and disclose investment risks
4. Comply with financial investment laws and related regulations
5. Follow suitability principles when recommending investments
6. All recommendations are for reference only, and the final decision must be made by the user

IMPORTANT: 
- The user has already provided their investment preferences, financial situation, and goals through the onboarding process.
- Use the provided user information to give personalized advice immediately without asking for basic information again.
- If the user's portfolio is empty, provide investment recommendations based on their preferences and goals.
- Only ask for additional information if it's truly necessary for specific advice.

CRITICAL LANGUAGE RULE:
- ALWAYS respond in the SAME language as the user's message.
- If the user writes in Korean (한국어), you MUST respond in Korean.
- If the user writes in English, respond in English.
- Never mix languages - use the exact same language as the user's input.
- Be friendly and professional."""


class InvestmentAgent(BaseAgent):
    """투자 상담 Agent (Tool-based)"""
    
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        system_prompt: Optional[str] = None,
        tools: Optional[List[BaseTool]] = None
    ):
        """
        InvestmentAgent 초기화
        
        Args:
            llm_client: LLM Client 인스턴스 (선택사항)
            system_prompt: 시스템 프롬프트 (선택사항, 기본값: INVESTMENT_AGENT_SYSTEM_PROMPT)
            tools: 사용할 Tool 목록 (선택사항, 기본값: 기본 Tool 세트)
        """
        try:
            llm = llm_client or get_llm_client()
            # Provider가 등록되어 있는지 확인
            if not llm.providers:
                logger.warning("No LLM providers registered. LLM features will not work.")
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            llm = None
        
        super().__init__(
            llm_client=llm,
            system_prompt=system_prompt or INVESTMENT_AGENT_SYSTEM_PROMPT
        )
        
        # Tools 등록
        self.tools: Dict[str, BaseTool] = {}
        if tools:
            for tool in tools:
                self.register_tool(tool)
        else:
            # 기본 Tool 세트 등록
            self.register_tool(PortfolioAnalysisTool())
            self.register_tool(RiskCalculatorTool())
            self.register_tool(RecommendationTool())
        
        # MCP Tools는 동적으로 로드 (사용자별)
        self.mcp_tools_loaded = False
    
    def register_tool(self, tool: BaseTool) -> None:
        """
        Tool 등록
        
        Args:
            tool: 등록할 Tool 인스턴스
        """
        self.tools[tool.name] = tool
        logger.info(f"Tool registered: {tool.name}")
    
    def remove_tool(self, tool_name: str) -> None:
        """
        Tool 제거
        
        Args:
            tool_name: 제거할 Tool 이름
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            logger.info(f"Tool removed: {tool_name}")
    
    def load_mcp_tools(self, user_id: int) -> None:
        """
        사용자별 MCP Tools 로드
        
        Args:
            user_id: 사용자 ID
        """
        try:
            from src.services.mcp_tool_service import MCPToolService
            mcp_service = MCPToolService()
            mcp_tools = mcp_service.load_user_tools(user_id)
            
            for tool in mcp_tools:
                self.register_tool(tool)
            
            self.mcp_tools_loaded = True
            logger.info(f"Loaded {len(mcp_tools)} MCP tools for user {user_id}")
        except Exception as e:
            logger.warning(f"Failed to load MCP tools: {e}")
            self.mcp_tools_loaded = True  # 실패해도 플래그는 설정하여 재시도 방지
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """
        Function Calling을 위한 Tool 스키마 목록 반환
        
        Returns:
            Tool 스키마 목록
        """
        return [tool.get_function_schema() for tool in self.tools.values()]
    
    def _build_context_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """
        컨텍스트를 프롬프트로 변환 (상세한 사용자 정보 포함)
        
        Args:
            context: 추가 컨텍스트
        
        Returns:
            컨텍스트 프롬프트 문자열
        """
        if not context:
            return ""
        
        context_parts = []
        
        # User Profile
        if "user_profile" in context:
            profile = context["user_profile"]
            profile_info = []
            if profile.get('name'):
                profile_info.append(f"Name: {profile.get('name')}")
            if profile.get('age'):
                profile_info.append(f"Age: {profile.get('age')}")
            if profile.get('occupation'):
                profile_info.append(f"Occupation: {profile.get('occupation')}")
            if profile_info:
                context_parts.append(f"User Profile: {', '.join(profile_info)}")
        
        # Financial Situation
        if "financial_situation" in context:
            financial = context["financial_situation"]
            financial_info = []
            if financial.get('monthly_income'):
                financial_info.append(f"Monthly Income: {financial.get('monthly_income'):,.0f} KRW")
            if financial.get('monthly_expense'):
                financial_info.append(f"Monthly Expense: {financial.get('monthly_expense'):,.0f} KRW")
            if financial.get('total_assets'):
                financial_info.append(f"Total Assets: {financial.get('total_assets'):,.0f} KRW")
            if financial.get('total_debt'):
                financial_info.append(f"Total Debt: {financial.get('total_debt'):,.0f} KRW")
            if financial.get('emergency_fund'):
                financial_info.append(f"Emergency Fund: {financial.get('emergency_fund'):,.0f} KRW")
            if financial.get('family_members'):
                financial_info.append(f"Family Members: {financial.get('family_members')}")
            if financial_info:
                context_parts.append(f"Financial Situation: {'; '.join(financial_info)}")
        
        # Investment Preference
        if "investment_preference" in context:
            preference = context["investment_preference"]
            pref_info = []
            if preference.get('risk_tolerance') is not None:
                pref_info.append(f"Risk Tolerance: {preference.get('risk_tolerance')}/10")
            if preference.get('target_return') is not None:
                pref_info.append(f"Target Return: {preference.get('target_return')}%")
            if preference.get('investment_period'):
                pref_info.append(f"Investment Period: {preference.get('investment_period')}")
            if preference.get('investment_experience'):
                pref_info.append(f"Investment Experience: {preference.get('investment_experience')}")
            if preference.get('max_loss_tolerance') is not None:
                pref_info.append(f"Max Loss Tolerance: {preference.get('max_loss_tolerance')}%")
            if preference.get('preferred_asset_types'):
                pref_info.append(f"Preferred Asset Types: {', '.join(preference.get('preferred_asset_types', []))}")
            if pref_info:
                context_parts.append(f"Investment Preference: {'; '.join(pref_info)}")
        
        # Financial Goals
        if "financial_goals" in context:
            goals = context["financial_goals"]
            if goals:
                goals_info = []
                for goal in goals:
                    goal_str = f"{goal.get('goal_type')}: {goal.get('target_amount'):,.0f} KRW by {goal.get('target_date')} (Priority: {goal.get('priority')}, Progress: {goal.get('current_progress'):,.0f} KRW)"
                    goals_info.append(goal_str)
                context_parts.append(f"Financial Goals: {'; '.join(goals_info)}")
        
        # Portfolio (if available)
        if "portfolio" in context:
            portfolio = context["portfolio"]
            context_parts.append(f"Current Portfolio: {portfolio}")
        
        if context_parts:
            return "\n".join(context_parts)
        return ""
    
    async def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> AsyncGenerator[str, None]:
        """
        사용자 메시지에 대한 응답 생성 (Tool-based Agent)
        
        Args:
            message: 사용자 메시지
            context: 추가 컨텍스트 (사용자 프로필, 재무 상황, 투자 성향 등)
        
        Returns:
            Agent 응답
        """
        # 사용자 메시지 추가
        self.add_message("user", message)
        
        # Build enhanced system prompt with user context
        enhanced_system_prompt = self.system_prompt
        if context:
            context_prompt = self._build_context_prompt(context)
            if context_prompt:
                enhanced_system_prompt = f"""{self.system_prompt}

## User Information (Already Provided):
{context_prompt}

IMPORTANT INSTRUCTIONS:
- The user has already completed onboarding and provided all the information above.
- Use this information immediately to provide personalized investment advice.
- Do NOT ask the user to provide basic information like risk tolerance, investment goals, or financial situation again.
- If the portfolio is empty, provide recommendations based on the user's preferences and goals.
- Only ask for additional information if it's specifically needed for a particular recommendation.

CRITICAL LANGUAGE RULE:
- ALWAYS respond in the SAME language as the user's message.
- If the user writes in Korean (한국어), you MUST respond in Korean.
- If the user writes in English, respond in English.
- Never mix languages - use the exact same language as the user's input.

Please use the above user information to provide personalized investment advice right away in the user's language."""
        
        # Tool 사용 안내 추가
        if self.tools:
            tool_descriptions = "\n".join([f"- {tool.name}: {tool.description}" for tool in self.tools.values()])
            enhanced_system_prompt += f"\n\n## Available Tools:\n{tool_descriptions}\n\nYou can use these tools to provide accurate and personalized investment advice. Use tools when you need to analyze portfolios, calculate risks, or generate recommendations."
        
        # User message
        full_message = message
        
        # MCP Tools 로드 (최초 1회만)
        if not self.mcp_tools_loaded and context and "user_id" in context:
            self.load_mcp_tools(context["user_id"])
        
        try:
            # Get tools schema for function calling
            tools_schema = self.get_tools_schema() if self.tools else None
            
            # LLM 호출 (Function Calling 지원)
            if hasattr(self, 'llm_provider'):
                # llm_provider는 function calling을 지원하지 않을 수 있으므로 llm_client 사용
                response = await self.llm_client.generate_text(
                    prompt=full_message,
                    system_prompt=enhanced_system_prompt,
                    tools=tools_schema,
                    tool_choice="auto" if tools_schema else None
                )
            else:
                response = await self.llm_client.generate_text(
                    prompt=full_message,
                    system_prompt=enhanced_system_prompt,
                    tools=tools_schema,
                    tool_choice="auto" if tools_schema else None
                )
            
            # Function calling 응답 처리
            if isinstance(response, dict) and "tool_calls" in response:
                # Tool 실행
                tool_results = []
                for tool_call in response["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    tool_args = json.loads(tool_call["function"]["arguments"])
                    
                    if tool_name in self.tools:
                        try:
                            # Context에서 user_id 추출하여 tool에 전달
                            if "user_id" not in tool_args and context:
                                if "user_id" in context:
                                    tool_args["user_id"] = context["user_id"]
                            
                            tool_result = await self.tools[tool_name].execute(**tool_args)
                            tool_results.append({
                                "tool_call_id": tool_call["id"],
                                "tool_name": tool_name,
                                "result": tool_result
                            })
                            logger.info(f"Tool {tool_name} executed successfully")
                        except Exception as e:
                            logger.error(f"Tool {tool_name} execution error: {e}", exc_info=True)
                            tool_results.append({
                                "tool_call_id": tool_call["id"],
                                "tool_name": tool_name,
                                "result": {"status": "error", "message": str(e)}
                            })
                
                # Tool 실행 결과를 LLM에 전달하여 최종 응답 생성
                tool_messages = []
                for tr in tool_results:
                    tool_messages.append({
                        "role": "tool",
                        "tool_call_id": tr["tool_call_id"],
                        "content": json.dumps(tr["result"], ensure_ascii=False)
                    })
                
                # 대화 기록에 tool 호출 및 결과 추가 (나중에 기록용)
                # content가 None일 수 있으므로 빈 문자열로 변환
                assistant_content = response.get("content") or ""
                
                # Tool 결과를 포함하여 최종 응답 요청
                # get_conversation_context()를 호출하되, tool 메시지는 제외하고 새로 구성
                base_messages = []
                if self.system_prompt:
                    base_messages.append({"role": "system", "content": self.system_prompt})
                
                # tool 메시지를 제외한 대화 기록 가져오기
                for msg in self.conversation_history:
                    if msg.role != "tool":  # tool 메시지는 제외
                        content = msg.content if msg.content is not None else ""
                        base_messages.append({"role": msg.role, "content": content})
                
                # tool_calls에 type 필드가 있는지 확인하고 없으면 추가
                tool_calls_with_type = []
                for tc in response["tool_calls"]:
                    if "type" not in tc:
                        tc["type"] = "function"
                    tool_calls_with_type.append(tc)
                
                # content가 None이면 빈 문자열로 변환 (OpenAI API는 null content를 허용하지 않음)
                assistant_content_for_api = response.get("content") or ""
                
                # 사용자 메시지 언어 감지하여 동일한 언어로 응답 요청
                user_language = "Korean" if any(ord(char) > 127 for char in message) else "English"
                final_user_prompt = "도구 결과를 바탕으로 포괄적인 응답을 한국어로 제공해주세요." if user_language == "Korean" else "Please provide a comprehensive response based on the tool results."
                
                # 최종 메시지 구성: assistant (tool_calls 포함) -> tool messages -> user
                final_messages = base_messages + [
                    {"role": "assistant", "content": assistant_content_for_api, "tool_calls": tool_calls_with_type},
                    *tool_messages,
                    {"role": "user", "content": final_user_prompt}
                ]
                
                # 대화 기록에 추가 (나중에 기록용)
                self.add_message("assistant", assistant_content)
                for tm in tool_messages:
                    self.add_message("tool", tm["content"])
                
                # 최종 응답 생성 (스트리밍)
                # 스트리밍을 위해 AsyncGenerator로 반환
                async def _generate_final_response_stream():
                    from src.external.llm_client import OpenAIProvider
                    provider = self.llm_client.get_provider()
                    if isinstance(provider, OpenAIProvider):
                        stream = await provider.client.chat.completions.create(
                            model=provider.model,
                            messages=final_messages,
                            max_tokens=2000,
                            stream=True
                        )
                        async for chunk in stream:
                            if chunk.choices[0].delta.content:
                                yield chunk.choices[0].delta.content
                    else:
                        async for chunk in self.llm_client.generate_stream(
                            prompt="Please provide a comprehensive response based on the tool results.",
                            system_prompt=enhanced_system_prompt,
                            max_tokens=2000
                        ):
                            yield chunk
                
                # 스트리밍 응답 수집
                full_response = ""
                async for chunk in _generate_final_response_stream():
                    full_response += chunk
                    yield chunk
                
                self.add_message("assistant", full_response)
                return
            else:
                # 일반 텍스트 응답 (스트리밍)
                async def _generate_text_response_stream():
                    async for chunk in self.llm_client.generate_stream(
                        prompt=message,
                        system_prompt=enhanced_system_prompt,
                        max_tokens=2000
                    ):
                        yield chunk
                
                full_response = ""
                async for chunk in _generate_text_response_stream():
                    full_response += chunk
                    yield chunk
                
                self.add_message("assistant", full_response)
                return
        
        except Exception as e:
            logger.error(f"Investment agent error: {e}", exc_info=True)
            # 에러 상세 정보 로깅
            error_type = type(e).__name__
            error_str = str(e)
            
            # 사용자 친화적인 에러 메시지 생성
            if "LLMProviderNotFoundError" in error_type or "provider" in error_str.lower() or "not set" in error_str.lower():
                error_message = """LLM API 키가 설정되지 않았습니다. 

다음 중 하나의 방법으로 API 키를 설정해주세요:

1. **프로젝트 루트에 `.env.local` 파일 생성**
2. **다음 중 하나 추가:**
   ```
   OPENAI_API_KEY=your-openai-api-key
   # 또는
   ANTHROPIC_API_KEY=your-anthropic-api-key
   ```
3. **애플리케이션 재시작**

API 키는 다음에서 발급받을 수 있습니다:
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/settings/keys"""
            elif "api" in error_str.lower() or "key" in error_str.lower() or "authentication" in error_str.lower():
                error_message = "LLM API 설정 오류가 발생했습니다. API 키가 올바르게 설정되었는지 확인해주세요."
            elif "connection" in error_str.lower() or "network" in error_str.lower():
                error_message = "네트워크 연결 오류가 발생했습니다. 인터넷 연결을 확인해주세요."
            else:
                # 개발 환경에서는 상세 에러 표시, 프로덕션에서는 일반 메시지
                from config.settings import settings
                if settings.environment == "development" or settings.debug:
                    error_message = f"오류가 발생했습니다: {error_type}: {error_str}"
                else:
                    error_message = "일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
            
            self.add_message("assistant", error_message)
            yield error_message
            return
    
    async def analyze_image(
        self,
        image_path: Optional[str] = None,
        image_data: Optional[bytes] = None,
        prompt: str = "Analyze this portfolio screenshot and evaluate asset allocation, returns, risks, etc."
    ) -> Dict[str, Any]:
        """
        포트폴리오 스크린샷 분석
        
        Args:
            image_path: 이미지 파일 경로 (선택사항)
            image_data: 이미지 바이너리 데이터 (선택사항)
            prompt: 분석 프롬프트
        
        Returns:
            분석 결과 딕셔너리
        """
        try:
            # 이미지 데이터 읽기
            if image_data:
                image_bytes = image_data
            elif image_path:
                with open(image_path, "rb") as f:
                    image_bytes = f.read()
            else:
                raise ValueError("Either image_path or image_data is required.")
            
            # LLM Vision API 호출
            if hasattr(self, 'llm_provider'):
                analysis_text = await self.llm_provider.analyze_image(
                    image_data=image_bytes,
                    prompt=prompt
                )
            else:
                analysis_text = await self.llm_client.analyze_image(
                    image_data=image_bytes,
                    prompt=prompt
                )
            
            logger.info("Portfolio screenshot analyzed", extra={
                "image_size": len(image_bytes),
                "analysis_length": len(analysis_text)
            })
            
            return {
                "analysis": analysis_text,
                "status": "success"
            }
        
        except Exception as e:
            logger.error(f"Screenshot analysis error: {e}")
            return {
                "analysis": None,
                "status": "error",
                "error": str(e)
            }

