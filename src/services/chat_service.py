"""
채팅 메시지 서비스
"""
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from config.database import Database, db
from config.logging import get_logger
from src.models.chat import ChatMessage
from src.repositories.chat_repository import ChatMessageRepository

logger = get_logger(__name__)


class ChatService:
    """채팅 메시지 서비스"""

    def __init__(self, database: Optional[Database] = None):
        """
        ChatService 초기화
        
        Args:
            database: Database 인스턴스 (기본값: 전역 db 인스턴스)
        """
        self.db = database or db
        self.chat_repo = ChatMessageRepository(self.db)

    async def get_messages(
        self,
        user_id: int,
        limit: Optional[int] = None,
        project_id: Optional[int] = None,
        session: Optional[AsyncSession] = None
    ) -> List[Dict[str, Any]]:
        """
        사용자의 채팅 메시지 조회
        
        Args:
            user_id: 사용자 ID
            limit: 최대 조회 개수 (None이면 전체)
            project_id: 프로젝트 ID (None이면 전체, 특정 프로젝트만 조회)
            session: 기존 세션 (선택사항)
        
        Returns:
            채팅 메시지 딕셔너리 리스트
        """
        messages = await self.chat_repo.get_by_user_id(user_id, limit=limit, project_id=project_id, session=session)

        result = []
        for msg in messages:
            message_dict = {
                "role": msg.role,
                "content": msg.content or "",  # None이면 빈 문자열
            }
            if msg.image_data:
                # base64 문자열을 bytes로 변환 (Streamlit st.image가 bytes를 기대)
                try:
                    import base64
                    import json
                    if isinstance(msg.image_data, str):
                        # JSON 형식으로 저장된 여러 이미지인지 확인
                        try:
                            image_list = json.loads(msg.image_data)
                            if isinstance(image_list, list):
                                # 여러 이미지 디코딩
                                decoded_images = []
                                for img_data in image_list:
                                    if isinstance(img_data, str):
                                        decoded_images.append(base64.b64decode(img_data))
                                    else:
                                        decoded_images.append(img_data)
                                message_dict["image"] = decoded_images
                            else:
                                # 단일 이미지 디코딩
                                message_dict["image"] = base64.b64decode(msg.image_data)
                        except (json.JSONDecodeError, ValueError):
                            # JSON이 아니면 단일 이미지로 처리
                            message_dict["image"] = base64.b64decode(msg.image_data)
                    else:
                        message_dict["image"] = msg.image_data
                except Exception as e:
                    logger.warning(f"Failed to decode image_data for message {msg.id}: {e}")
            if msg.image_caption:
                # 여러 캡션인지 확인 (JSON 형식)
                try:
                    import json
                    captions = json.loads(msg.image_caption)
                    if isinstance(captions, list):
                        message_dict["image_captions"] = captions
                    else:
                        message_dict["image_caption"] = msg.image_caption
                except (json.JSONDecodeError, ValueError):
                    message_dict["image_caption"] = msg.image_caption

            result.append(message_dict)

        logger.debug(f"Converted {len(result)} messages to dict format")
        # 최신순이므로 역순으로 반환 (오래된 것부터)
        return list(reversed(result))

    async def save_message(
        self,
        user_id: int,
        role: str,
        content: str,
        image_data: Optional[str] = None,
        image_caption: Optional[str] = None,
        project_id: Optional[int] = None,
        session: Optional[AsyncSession] = None
    ) -> ChatMessage:
        """
        채팅 메시지 저장
        
        Args:
            user_id: 사용자 ID
            role: 메시지 역할 (user, assistant, system)
            content: 메시지 내용
            image_data: 이미지 데이터 (base64 또는 파일 경로, 선택사항)
            image_caption: 이미지 캡션 (선택사항)
            session: 기존 세션 (선택사항)
        
        Returns:
            저장된 ChatMessage 객체
        """
        # 이미지 데이터 처리 (bytes 또는 리스트)
        if image_data:
            import base64
            import json
            if isinstance(image_data, list):
                # 여러 이미지: JSON 배열로 저장
                encoded_images = []
                for img in image_data:
                    if isinstance(img, bytes):
                        encoded_images.append(base64.b64encode(img).decode('utf-8'))
                    elif isinstance(img, str):
                        # 이미 base64 문자열인 경우
                        encoded_images.append(img)
                    else:
                        encoded_images.append(img)
                image_data = json.dumps(encoded_images)
            elif isinstance(image_data, bytes):
                # 단일 이미지: base64로 변환
                image_data = base64.b64encode(image_data).decode('utf-8')
            # str 타입이고 이미 JSON인 경우 그대로 사용

        # 이미지 캡션 처리 (여러 캡션 지원)
        if image_caption:
            import json
            if isinstance(image_caption, list):
                # 여러 캡션: JSON 배열로 저장
                image_caption = json.dumps(image_caption)
            # 단일 캡션은 문자열로 그대로 저장

        message = await self.chat_repo.create_message(
            user_id=user_id,
            role=role,
            content=content,
            image_data=image_data,
            image_caption=image_caption,
            project_id=project_id,
            session=session
        )

        logger.info(f"Chat message saved: user_id={user_id}, role={role}, content_length={len(content)}")
        return message

    async def clear_messages(
        self,
        user_id: int,
        project_id: Optional[int] = None,
        session: Optional[AsyncSession] = None
    ) -> int:
        """
        사용자의 채팅 메시지 삭제
        
        Args:
            user_id: 사용자 ID
            project_id: 프로젝트 ID (None이면 전체 삭제, 특정 프로젝트만 삭제)
            session: 기존 세션 (선택사항)
        
        Returns:
            삭제된 메시지 개수
        """
        if project_id is None:
            count = await self.chat_repo.delete_by_user_id(user_id, session=session)
        else:
            # 프로젝트별 삭제
            from sqlalchemy import delete

            from src.models.chat import ChatMessage
            query = delete(ChatMessage).where(
                ChatMessage.user_id == user_id,
                ChatMessage.project_id == project_id
            )
            if session:
                result = await session.execute(query)
                await session.flush()
                count = result.rowcount
            else:
                async with self.db.session() as session:
                    result = await session.execute(query)
                    await session.flush()
                    count = result.rowcount

        logger.info(f"Cleared {count} chat messages for user_id={user_id}, project_id={project_id}")
        return count

    async def search_messages(
        self,
        user_id: int,
        search_query: str,
        project_id: Optional[int] = None,
        limit: Optional[int] = 50,
        session: Optional[AsyncSession] = None
    ) -> List[Dict[str, Any]]:
        """
        채팅 메시지 검색
        
        Args:
            user_id: 사용자 ID
            search_query: 검색어
            project_id: 프로젝트 ID (None이면 전체 검색)
            limit: 최대 결과 개수
            session: 기존 세션 (선택사항)
        
        Returns:
            검색된 메시지 딕셔너리 리스트
        """
        from sqlalchemy import desc, select

        from src.models.chat import ChatMessage

        query = select(ChatMessage).where(
            ChatMessage.user_id == user_id,
            ChatMessage.content.contains(search_query)
        )

        if project_id is not None:
            query = query.where(ChatMessage.project_id == project_id)

        query = query.order_by(desc(ChatMessage.created_at))

        if limit:
            query = query.limit(limit)

        if session:
            result = await session.execute(query)
            messages = list(result.scalars().all())
        else:
            async with self.db.session() as session:
                result = await session.execute(query)
                messages = list(result.scalars().all())

        # 딕셔너리로 변환
        result_list = []
        for msg in messages:
            message_dict = {
                "role": msg.role,
                "content": msg.content or "",
            }
            if msg.image_data:
                try:
                    import base64
                    import json
                    if isinstance(msg.image_data, str):
                        # JSON 형식으로 저장된 여러 이미지인지 확인
                        try:
                            image_list = json.loads(msg.image_data)
                            if isinstance(image_list, list):
                                # 여러 이미지 디코딩
                                decoded_images = []
                                for img_data in image_list:
                                    if isinstance(img_data, str):
                                        decoded_images.append(base64.b64decode(img_data))
                                    else:
                                        decoded_images.append(img_data)
                                message_dict["image"] = decoded_images
                            else:
                                # 단일 이미지 디코딩
                                message_dict["image"] = base64.b64decode(msg.image_data)
                        except (json.JSONDecodeError, ValueError):
                            # JSON이 아니면 단일 이미지로 처리
                            message_dict["image"] = base64.b64decode(msg.image_data)
                    else:
                        message_dict["image"] = msg.image_data
                except Exception as e:
                    logger.warning(f"Failed to decode image_data for message {msg.id}: {e}")
            if msg.image_caption:
                # 여러 캡션인지 확인 (JSON 형식)
                try:
                    import json
                    captions = json.loads(msg.image_caption)
                    if isinstance(captions, list):
                        message_dict["image_captions"] = captions
                    else:
                        message_dict["image_caption"] = msg.image_caption
                except (json.JSONDecodeError, ValueError):
                    message_dict["image_caption"] = msg.image_caption

            result_list.append(message_dict)

        return list(reversed(result_list))

