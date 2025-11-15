"""
채팅 메시지 모델
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.chat_project import ChatProject


class ChatMessage(Base, TimestampMixin):
    """채팅 메시지 모델"""
    
    __tablename__ = "chat_messages"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    image_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # base64 encoded image or file path
    image_caption: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    project_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("chat_projects.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # 관계
    user: Mapped["User"] = relationship("User", back_populates="chat_messages")
    project: Mapped[Optional["ChatProject"]] = relationship("ChatProject", back_populates="chat_messages")
    
    def __repr__(self) -> str:
        return f"<ChatMessage(id={self.id}, user_id={self.user_id}, role={self.role}, content_length={len(self.content)})>"

