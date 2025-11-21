"""
Agent Chat Page
"""
import streamlit as st

from config.database import db
from config.logging import get_logger
from src.agents import InvestmentAgent
from src.middleware import auth_middleware
from src.repositories import FinancialGoalRepository, FinancialSituationRepository
from src.services import ChatService, InvestmentPreferenceService, UserService
from src.utils.async_helpers import run_async
from src.utils.chat_ui import render_chat_file_upload_script, render_chat_file_upload_styles

logger = get_logger(__name__)

st.set_page_config(
    page_title="Agent Chat - BUJA",
    page_icon="🤖",
    layout="wide"
)

# Authentication check
if not auth_middleware.is_authenticated():
    st.warning("Login required.")
    st.switch_page("pages/login.py")
    st.stop()

user = auth_middleware.get_current_user()

# Initialize services
user_service = UserService()
preference_service = InvestmentPreferenceService()

# Check if user needs onboarding (first-time user check)
try:
    user_with_profile = run_async(user_service.get_user_with_profile(user.id))
    preference = run_async(preference_service.get_preference(user.id))
    financial_situation_repo = FinancialSituationRepository(db)
    financial_goal_repo = FinancialGoalRepository(db)

    has_profile = user_with_profile.profile is not None
    has_preference = preference is not None
    has_financial_situation = False
    has_financial_goals = False

    try:
        financial_situation = run_async(financial_situation_repo.get_by_user_id(user.id))
        has_financial_situation = financial_situation is not None
    except Exception as e:
        logger.debug(f"Could not load financial situation: {e}")
        pass

    try:
        financial_goals = run_async(financial_goal_repo.get_by_user_id(user.id))
        has_financial_goals = len(financial_goals) > 0 if financial_goals else False
    except Exception as e:
        logger.debug(f"Could not load financial goals: {e}")
        pass

    # Redirect if onboarding is not completed
    if not has_profile or not has_preference or not has_financial_situation:
        if "onboarding_completed" not in st.session_state:
            st.info("👋 Welcome! Please complete your basic information first.")
            st.switch_page("pages/onboarding.py")
            st.stop()
except Exception as e:
    # Continue even if onboarding check fails (only log error)
    logger.warning(f"Onboarding check failed, continuing anyway: {e}", exc_info=True)

# Initialize services
chat_service = ChatService()

# Load chat history from database
# 새로고침 시에도 항상 데이터베이스에서 로드
if "messages" not in st.session_state:
    st.session_state.messages = []

# 현재 프로젝트 ID 확인
current_project_id = st.session_state.get("current_project_id", None)

# 항상 데이터베이스에서 최신 메시지 로드 (새로고침 대응)
try:
    saved_messages = run_async(chat_service.get_messages(user.id, project_id=current_project_id))
    logger.debug(f"Retrieved {len(saved_messages) if saved_messages else 0} messages from database for user {user.id}")

    if saved_messages and len(saved_messages) > 0:
        # 데이터베이스 메시지로 교체 (중복 방지)
        st.session_state.messages = saved_messages
        logger.info(f"Loaded {len(saved_messages)} messages from database for user {user.id}")

        # 디버깅: 첫 번째 메시지 내용 확인
        if len(saved_messages) > 0:
            first_msg = saved_messages[0]
            logger.debug(f"First message: role={first_msg.get('role')}, content_length={len(first_msg.get('content', ''))}")
    else:
        # 저장된 메시지가 없으면 빈 리스트로 시작
        if not st.session_state.messages or len(st.session_state.messages) == 0:
            st.session_state.messages = []
            logger.info(f"No saved messages found for user {user.id}, starting with empty chat")
except Exception as e:
    logger.error(f"Could not load chat history: {e}", exc_info=True)
    if not st.session_state.messages:
        st.session_state.messages = []

# Initialize agent
if "agent" not in st.session_state:
    try:
        st.session_state.agent = InvestmentAgent()
    except Exception as e:
        logger.error(f"Failed to initialize InvestmentAgent: {e}", exc_info=True)
        st.error(f"❌ Failed to initialize agent: {str(e)}")
        st.stop()

st.title("🤖 Investment Agent Chat")

# 공통 사이드바 렌더링 (agent_chat 페이지임을 전달)
try:
    from src.utils.sidebar import render_sidebar
    render_sidebar(current_page="agent_chat")
except Exception as e:
    logger.error(f"Failed to render sidebar: {e}", exc_info=True)
    # Continue even if sidebar fails
    pass

# Display chat history
if st.session_state.messages:
    logger.debug(f"Displaying {len(st.session_state.messages)} messages")
    for idx, message in enumerate(st.session_state.messages):
        try:
            with st.chat_message(message["role"]):
                # 이미지 표시 (user와 assistant 모두 지원)
                if "image" in message:
                    # 단일 이미지
                    if isinstance(message["image"], bytes):
                        st.image(
                            message["image"],
                            caption=message.get("image_caption", ""),
                            use_container_width=True
                        )
                    # 여러 이미지 (리스트)
                    elif isinstance(message["image"], list):
                        for img_idx, img in enumerate(message["image"]):
                            if isinstance(img, bytes):
                                caption = ""
                                if "image_captions" in message and isinstance(message["image_captions"], list):
                                    if img_idx < len(message["image_captions"]):
                                        caption = message["image_captions"][img_idx]
                                elif "image_caption" in message:
                                    caption = message["image_caption"]
                                st.image(img, caption=caption, use_container_width=True)
                # Display empty string if content is None
                content = message.get("content") or ""
                if content:
                    st.write(content)
        except Exception as e:
            logger.error(f"Error displaying message {idx}: {e}", exc_info=True)
            # 에러가 있어도 계속 진행
            pass
else:
    logger.debug("No messages to display")

# 파일 업로더가 하단에 보이도록 빈 공간 추가
st.markdown("<br><br><br><br><br><br><br><br>", unsafe_allow_html=True)

# 이미지 업로드 상태 관리 (여러 이미지 지원)
if "uploaded_images" not in st.session_state:
    st.session_state.uploaded_images = []  # [(image_data, image_name), ...]

# 파일 업로드 UI 스타일 및 스크립트 렌더링
render_chat_file_upload_styles()
render_chat_file_upload_script()

# 업로드된 이미지가 있으면 썸네일 표시
if st.session_state.uploaded_images:
    for img_idx, (img_data, img_name) in enumerate(st.session_state.uploaded_images):
        thumb_col, name_col, remove_col = st.columns([1, 18, 1])
        with thumb_col:
            st.image(img_data, width=40, use_container_width=False)
        with name_col:
            st.caption(f"📎 {img_name}")
        with remove_col:
            if st.button("❌", key=f"remove_image_{img_idx}", help="제거"):
                st.session_state.uploaded_images.pop(img_idx)
                st.rerun()

# 파일 업로드 (여러 파일 선택 가능)
# 방법 1: 📎 아이콘 클릭 (채팅 입력창 왼쪽)
# 방법 2: 아래 파일 업로더 버튼 사용
uploaded_files = st.file_uploader(
    "📎 이미지 업로드 (여러 파일 선택 가능)",
    type=["png", "jpg", "jpeg", "gif", "webp"],
    help="이미지 파일을 업로드하세요. 여러 파일을 동시에 선택할 수 있습니다.",
    key="image_uploader",
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        # 중복 체크
        file_name = uploaded_file.name
        if not any(name == file_name for _, name in st.session_state.uploaded_images):
            img_data = uploaded_file.read()
            st.session_state.uploaded_images.append((img_data, file_name))
    st.rerun()

# Chat input (입력창)
prompt = st.chat_input("무엇이든 물어보세요...")

if prompt or st.session_state.uploaded_images:
    # Analyze images if present
    image_data = None
    image_captions = []

    if st.session_state.uploaded_images:
        # 여러 이미지 지원
        if len(st.session_state.uploaded_images) == 1:
            # 단일 이미지
            image_data = st.session_state.uploaded_images[0][0]
            image_captions = [st.session_state.uploaded_images[0][1] or "uploaded_image"]
        else:
            # 여러 이미지
            image_data = [img[0] for img in st.session_state.uploaded_images]
            image_captions = [img[1] or f"image_{idx+1}" for idx, img in enumerate(st.session_state.uploaded_images)]

        # 이미지 사용 후 초기화
        st.session_state.uploaded_images = []

    # Add user message
    user_message = {
        "role": "user",
        "content": prompt or ("Please analyze this image." if image_data else "")
    }
    if image_data:
        user_message["image"] = image_data
        if len(image_captions) == 1:
            user_message["image_caption"] = image_captions[0]
        else:
            user_message["image_captions"] = image_captions

    st.session_state.messages.append(user_message)

    # Save user message to database
    # 여러 이미지 모두 저장 (JSON 배열로 저장)
    try:
        save_image_data = None
        save_image_caption = None
        if image_data:
            if isinstance(image_data, list):
                # 여러 이미지: 리스트로 전달 (서비스에서 JSON으로 변환)
                save_image_data = image_data
                save_image_caption = image_captions if len(image_captions) > 1 else (image_captions[0] if image_captions else None)
            else:
                # 단일 이미지
                save_image_data = image_data
                save_image_caption = image_captions[0] if image_captions else None

        saved_msg = run_async(chat_service.save_message(
            user_id=user.id,
            role="user",
            content=user_message["content"],
            image_data=save_image_data,
            image_caption=save_image_caption,
            project_id=st.session_state.get("current_project_id")
        ))
        logger.info(f"User message saved successfully: id={saved_msg.id if hasattr(saved_msg, 'id') else 'N/A'}")
    except Exception as e:
        logger.error(f"Failed to save user message: {e}", exc_info=True)
        st.warning(f"Failed to save message: {str(e)}")

    with st.chat_message("user"):
        if image_data:
            if isinstance(image_data, list):
                # 여러 이미지 표시
                for img_idx, img in enumerate(image_data):
                    caption = image_captions[img_idx] if img_idx < len(image_captions) else ""
                    st.image(img, caption=caption, use_container_width=True)
            else:
                # 단일 이미지 표시
                caption = image_captions[0] if image_captions else ""
                st.image(image_data, caption=caption, use_container_width=True)
        if prompt:
            st.write(prompt)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Analyze images if present
                if image_data:
                    try:
                        # 여러 이미지인 경우 첫 번째 이미지만 분석 (또는 모든 이미지 분석)
                        analyze_image = image_data[0] if isinstance(image_data, list) else image_data

                        analysis_result = run_async(
                            st.session_state.agent.analyze_image(
                                image_data=analyze_image,
                                prompt=prompt or "Please analyze this portfolio screenshot and provide investment advice."
                            )
                        )

                        if analysis_result.get("status") == "success":
                            analysis_text = analysis_result.get("analysis", "")

                            # 분석 결과에 이미지 포함 (필요한 경우)
                            assistant_msg = {
                                "role": "assistant",
                                "content": f"📊 Image Analysis Result:\n\n{analysis_text}"
                            }

                            # 분석 결과 이미지가 있으면 포함
                            if "image" in analysis_result:
                                assistant_msg["image"] = analysis_result["image"]
                                if "image_caption" in analysis_result:
                                    assistant_msg["image_caption"] = analysis_result["image_caption"]

                            # Assistant 메시지에 이미지 표시
                            if "image" in assistant_msg:
                                if isinstance(assistant_msg["image"], list):
                                    for img_idx, img in enumerate(assistant_msg["image"]):
                                        caption = ""
                                        if "image_captions" in assistant_msg and isinstance(assistant_msg["image_captions"], list):
                                            if img_idx < len(assistant_msg["image_captions"]):
                                                caption = assistant_msg["image_captions"][img_idx]
                                        elif "image_caption" in assistant_msg:
                                            caption = assistant_msg["image_caption"]
                                        st.image(img, caption=caption, use_container_width=True)
                                else:
                                    caption = assistant_msg.get("image_caption", "")
                                    st.image(assistant_msg["image"], caption=caption, use_container_width=True)

                            st.write("📊 **Image Analysis Result:**")
                            st.write(analysis_text)

                            st.session_state.messages.append(assistant_msg)

                            # Save assistant message to database
                            try:
                                saved_msg = run_async(chat_service.save_message(
                                    user_id=user.id,
                                    role="assistant",
                                    content=assistant_msg["content"],
                                    image_data=assistant_msg.get("image"),
                                    image_caption=assistant_msg.get("image_caption"),
                                    project_id=st.session_state.get("current_project_id")
                                ))
                                logger.info(f"Image analysis message saved successfully: id={saved_msg.id if hasattr(saved_msg, 'id') else 'N/A'}")
                            except Exception as e:
                                logger.error(f"Failed to save image analysis message: {e}", exc_info=True)
                        else:
                            error_msg = analysis_result.get("error", "An error occurred during image analysis.")
                            st.error(f"Image Analysis Error: {error_msg}")
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": f"Image Analysis Error: {error_msg}"
                            })
                    except Exception as e:
                        st.error(f"Error during image analysis: {str(e)}")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"Error during image analysis: {str(e)}"
                        })

                # Generate regular chat response if text prompt exists
                if prompt:
                    # Build context with all user information (optimized: single session)
                    context = {}
                    try:
                        # 모든 쿼리를 하나의 세션으로 묶어서 최적화
                        async def load_user_context():
                            async with db.session() as session:
                                user_with_profile = await user_service.get_user_with_profile(user.id)
                                preference = await preference_service.get_preference(user.id)
                                financial_situation_repo = FinancialSituationRepository(db)
                                financial_goal_repo = FinancialGoalRepository(db)

                                # User Profile
                                if user_with_profile and user_with_profile.profile:
                                    context["user_profile"] = {
                                        "name": user_with_profile.profile.name,
                                        "age": user_with_profile.profile.age,
                                        "occupation": user_with_profile.profile.occupation,
                                    }

                                # Investment Preference
                                if preference:
                                    context["investment_preference"] = {
                                        "risk_tolerance": preference.risk_tolerance,
                                        "target_return": float(preference.target_return) if preference.target_return else None,
                                        "investment_period": preference.investment_period,
                                        "investment_experience": preference.investment_experience,
                                        "max_loss_tolerance": float(preference.max_loss_tolerance) if preference.max_loss_tolerance else None,
                                        "preferred_asset_types": preference.preferred_asset_types or [],
                                    }

                                # Financial Situation
                                try:
                                    financial_situation = await financial_situation_repo.get_by_user_id(user.id, session=session)
                                    if financial_situation:
                                        context["financial_situation"] = {
                                            "monthly_income": float(financial_situation.monthly_income) if financial_situation.monthly_income else None,
                                            "monthly_expense": float(financial_situation.monthly_expense) if financial_situation.monthly_expense else None,
                                            "total_assets": float(financial_situation.total_assets) if financial_situation.total_assets else None,
                                            "total_debt": float(financial_situation.total_debt) if financial_situation.total_debt else None,
                                            "emergency_fund": float(financial_situation.emergency_fund) if financial_situation.emergency_fund else None,
                                            "family_members": financial_situation.family_members,
                                            "insurance_coverage": float(financial_situation.insurance_coverage) if financial_situation.insurance_coverage else None,
                                        }
                                except Exception as e:
                                    logger.debug(f"Could not load financial situation: {e}")

                                # Financial Goals
                                try:
                                    financial_goals = await financial_goal_repo.get_by_user_id(user.id, session=session)
                                    if financial_goals:
                                        context["financial_goals"] = [
                                            {
                                                "goal_type": goal.goal_type,
                                                "target_amount": float(goal.target_amount),
                                                "target_date": goal.target_date.isoformat(),
                                                "priority": goal.priority,
                                                "current_progress": float(goal.current_progress),
                                            }
                                            for goal in financial_goals
                                        ]
                                except Exception as e:
                                    logger.debug(f"Could not load financial goals: {e}")

                                # Add user_id (required for tool execution)
                                context["user_id"] = user.id
                                return context

                        context = run_async(load_user_context())

                    except Exception as e:
                        logger.warning(f"Could not load full user context: {str(e)}", exc_info=True)
                        # Add user_id at minimum
                        context = {"user_id": user.id}

                    # Debug: check context
                    if st.session_state.get("debug_mode", False):
                        st.json(context)

                    # Generate agent response (streaming)
                    response_placeholder = st.empty()

                    # Collect and display streaming response
                    full_response_list = []

                    async def stream_response():
                        try:
                            async for chunk in st.session_state.agent.chat(prompt, context=context):
                                full_response_list.append(chunk)
                                current_response = "".join(full_response_list)
                                response_placeholder.write(current_response)
                        except Exception as e:
                            logger.error(f"Streaming error: {e}")
                            error_msg = f"An error occurred: {str(e)}"
                            if not full_response_list:
                                full_response_list.append(error_msg)
                            response_placeholder.write("".join(full_response_list))

                    run_async(stream_response())

                    full_response = "".join(full_response_list)

                    if not image_data:  # Prevent duplicate display if image analysis result already shown
                        if full_response:
                            response_placeholder.write(full_response)

                    assistant_message = {"role": "assistant", "content": full_response}
                    st.session_state.messages.append(assistant_message)

                    # Save assistant message to database
                    try:
                        saved_msg = run_async(chat_service.save_message(
                            user_id=user.id,
                            role="assistant",
                            content=full_response,
                            project_id=st.session_state.get("current_project_id")
                        ))
                        logger.info(f"Assistant message saved successfully: id={saved_msg.id if hasattr(saved_msg, 'id') else 'N/A'}")
                    except Exception as e:
                        logger.error(f"Failed to save assistant message: {e}", exc_info=True)
                        st.warning(f"Failed to save message: {str(e)}")
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

