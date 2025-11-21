"""
이메일 알림 서비스
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from config.database import db
from config.logging import get_logger
from config.settings import settings
from src.models.notification import Notification
from src.repositories import UserRepository

logger = get_logger(__name__)


class EmailNotificationService:
    """이메일 알림 서비스"""
    
    def __init__(self):
        self.user_repo = UserRepository(db)
        # 이메일 설정 (환경 변수에서 로드)
        self.smtp_host = getattr(settings, 'smtp_host', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'smtp_port', 587)
        self.smtp_user = getattr(settings, 'smtp_user', None)
        self.smtp_password = getattr(settings, 'smtp_password', None)
        self.from_email = getattr(settings, 'from_email', self.smtp_user)
        self.from_name = getattr(settings, 'from_name', 'BUJA 투자 상담')
    
    async def send_notification_email(
        self,
        user_id: int,
        notification: Notification
    ) -> bool:
        """
        알림 이메일 전송
        
        Args:
            user_id: 사용자 ID
            notification: 알림 객체
        
        Returns:
            전송 성공 여부
        """
        try:
            # 사용자 정보 조회
            user = await self.user_repo.get_by_id(user_id)
            if not user or not user.email:
                logger.warning(f"User {user_id} not found or has no email")
                return False
            
            # SMTP 설정이 없으면 스킵
            if not self.smtp_user or not self.smtp_password:
                logger.debug("SMTP not configured, skipping email notification")
                return False
            
            # 이메일 내용 생성
            subject = f"[BUJA] {notification.title}"
            body = self._create_email_body(notification)
            
            # 이메일 전송
            success = self._send_email(
                to_email=user.email,
                subject=subject,
                body=body
            )
            
            if success:
                logger.info(f"Email notification sent to {user.email} for notification {notification.id}")
            else:
                logger.warning(f"Failed to send email notification to {user.email}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending email notification: {e}", exc_info=True)
            return False
    
    def _create_email_body(self, notification: Notification) -> str:
        """이메일 본문 생성"""
        # HTML 형식 이메일
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background-color: #f9f9f9;
                    padding: 20px;
                    border-radius: 0 0 5px 5px;
                }}
                .notification-type {{
                    display: inline-block;
                    background-color: #2196F3;
                    color: white;
                    padding: 5px 10px;
                    border-radius: 3px;
                    font-size: 12px;
                    margin-bottom: 10px;
                }}
                .message {{
                    background-color: white;
                    padding: 15px;
                    border-left: 4px solid #4CAF50;
                    margin: 15px 0;
                }}
                .footer {{
                    text-align: center;
                    color: #666;
                    font-size: 12px;
                    margin-top: 20px;
                }}
                .button {{
                    display: inline-block;
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 15px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>💰 BUJA 투자 상담</h1>
            </div>
            <div class="content">
                <div class="notification-type">{notification.type.value}</div>
                <h2>{notification.title}</h2>
                <div class="message">
                    {notification.message.replace(chr(10), '<br>')}
                </div>
                <a href="https://buja.app/agent_chat" class="button">앱에서 확인하기</a>
            </div>
            <div class="footer">
                <p>이 메일은 BUJA 투자 상담 서비스에서 자동으로 발송되었습니다.</p>
                <p>알림 설정을 변경하려면 앱의 설정 메뉴를 이용하세요.</p>
            </div>
        </body>
        </html>
        """
        
        return html_body
    
    def _send_email(
        self,
        to_email: str,
        subject: str,
        body: str
    ) -> bool:
        """
        실제 이메일 전송
        
        Args:
            to_email: 수신자 이메일
            subject: 제목
            body: 본문 (HTML)
        
        Returns:
            전송 성공 여부
        """
        try:
            # 메시지 생성
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # HTML 본문 추가
            html_part = MIMEText(body, 'html', 'utf-8')
            msg.attach(html_part)
            
            # SMTP 서버 연결 및 전송
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            logger.error(f"SMTP error: {e}", exc_info=True)
            return False

