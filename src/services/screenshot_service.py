"""
스크린샷 분석 서비스
"""
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
from io import BytesIO
from PIL import Image
from config.database import Database, db
from src.repositories import ScreenshotRepository
from src.models import Screenshot
from src.services.user_service import UserService
from src.external.llm_client import get_llm_client
from src.exceptions import (
    UserNotFoundError,
    ValidationError,
    InvalidImageFormatError,
    ImageUploadError,
    ScreenshotAnalysisError,
)
from config.settings import settings
from config.logging import get_logger

logger = get_logger(__name__)


class ScreenshotService:
    """스크린샷 분석 서비스"""
    
    def __init__(self, database: Optional[Database] = None):
        """
        ScreenshotService 초기화
        
        Args:
            database: Database 인스턴스 (기본값: 전역 db 인스턴스)
        """
        self.db = database or db
        self.screenshot_repo = ScreenshotRepository(self.db)
        self.user_service = UserService(self.db)
        self.llm_client = get_llm_client()
    
    def validate_image(
        self,
        image_data: bytes,
        max_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        이미지 검증
        
        Args:
            image_data: 이미지 바이너리 데이터
            max_size: 최대 크기 (바이트, 기본값: settings.max_upload_size)
        
        Returns:
            검증 결과 딕셔너리
        
        Raises:
            InvalidImageFormatError: 이미지 형식이 잘못된 경우
            ImageUploadError: 이미지 크기가 초과된 경우
        """
        max_size = max_size or settings.max_upload_size
        
        # 크기 검증
        if len(image_data) > max_size:
            raise ImageUploadError(f"이미지 크기가 {max_size / 1024 / 1024:.1f}MB를 초과합니다.")
        
        # 이미지 형식 검증
        try:
            image = Image.open(BytesIO(image_data))
            image.verify()
            
            # MIME 타입 확인
            image_format = image.format
            mime_type = f"image/{image_format.lower()}" if image_format else None
            
            if mime_type not in settings.allowed_image_types:
                raise InvalidImageFormatError(f"허용되지 않은 이미지 형식입니다: {mime_type}")
            
            return {
                "valid": True,
                "format": image_format,
                "mime_type": mime_type,
                "size": len(image_data),
                "width": image.width,
                "height": image.height
            }
        except Exception as e:
            logger.error(f"Image validation failed: {e}")
            raise InvalidImageFormatError(f"Image validation failed: {str(e)}")
    
    async def upload_screenshot(
        self,
        user_id: int,
        image_data: bytes,
        app_type: Optional[str] = None,
        file_name: Optional[str] = None
    ) -> Screenshot:
        """
        스크린샷 업로드
        
        Args:
            user_id: 사용자 ID
            image_data: 이미지 바이너리 데이터
            app_type: 앱 유형 (KEYUM, NH, UPBIT 등, 선택사항)
            file_name: 파일 이름 (선택사항)
        
        Returns:
            생성된 Screenshot 객체
        
        Raises:
            UserNotFoundError: 사용자를 찾을 수 없는 경우
            InvalidImageFormatError: 이미지 형식이 잘못된 경우
        """
        # 사용자 존재 확인
        await self.user_service.get_user(user_id)
        
        # 이미지 검증
        validation_result = self.validate_image(image_data)
        
        # 파일 저장 경로 생성
        file_name = file_name or f"screenshot_{user_id}_{datetime.now().timestamp()}.{validation_result['format'].lower()}"
        file_path = Path(settings.data_dir if hasattr(settings, 'data_dir') else "data") / "screenshots" / file_name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 이미지 저장
        try:
            with open(file_path, "wb") as f:
                f.write(image_data)
        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            raise ImageUploadError(f"Failed to save image: {str(e)}")
        
        # 데이터베이스에 기록
        async with self.db.session() as session:
            screenshot = Screenshot(
                user_id=user_id,
                file_path=str(file_path),
                file_size=len(image_data),
                app_type=app_type,
                analysis_status="PENDING"
            )
            screenshot = await self.screenshot_repo.create(screenshot, session=session)
            await session.commit()
            await session.refresh(screenshot)
            
            logger.info(f"Screenshot uploaded: user_id={user_id}, screenshot_id={screenshot.id}")
            return screenshot
    
    async def analyze_screenshot(
        self,
        screenshot_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """
        스크린샷 분석
        
        Args:
            screenshot_id: 스크린샷 ID
            user_id: 사용자 ID
        
        Returns:
            분석 결과 딕셔너리
        
        Raises:
            ScreenshotAnalysisError: 분석 실패 시
        """
        # 스크린샷 조회 및 소유권 확인
        screenshot = await self.screenshot_repo.get_by_id(screenshot_id)
        if not screenshot:
            raise ValidationError(f"Screenshot not found: {screenshot_id}")
        
        if screenshot.user_id != user_id:
            raise ValidationError("본인의 스크린샷만 분석할 수 있습니다.")
        
        # 분석 상태 업데이트
        async with self.db.session() as session:
            screenshot.analysis_status = "PROCESSING"
            await self.screenshot_repo.update(screenshot, session=session)
            await session.commit()
        
        try:
            # 이미지 읽기
            with open(screenshot.file_path, "rb") as f:
                image_data = f.read()
            
            # LLM Vision API로 분석
            analysis_prompt = """
            이 포트폴리오 스크린샷을 분석하여 다음 정보를 JSON 형식으로 추출해주세요:
            - 자산 유형별 비중 (주식, 채권, 현금, 펀드 등)
            - 종목별 보유 비중 (있는 경우)
            - 현재 자산 가치
            - 수익률 (총 수익률, 일일 수익률 등)
            - 매수 평균가 및 현재가
            - 수수료 및 비용 정보
            - 거래 내역 (가능한 경우)
            
            JSON 형식으로만 응답해주세요.
            """
            
            analysis_text = await self.llm_client.analyze_image(
                image_data=image_data,
                prompt=analysis_prompt
            )
            
            # JSON 파싱 시도
            import json
            try:
                extracted_data = json.loads(analysis_text)
            except json.JSONDecodeError:
                # JSON이 아니면 텍스트로 저장
                extracted_data = {"raw_analysis": analysis_text}
            
            # 분석 결과 저장
            async with self.db.session() as session:
                screenshot.extracted_data = extracted_data
                screenshot.analysis_status = "COMPLETED"
                await self.screenshot_repo.update(screenshot, session=session)
                await session.commit()
                await session.refresh(screenshot)
            
            logger.info(f"Screenshot analyzed: screenshot_id={screenshot_id}")
            
            return {
                "screenshot_id": screenshot_id,
                "extracted_data": extracted_data,
                "status": "success"
            }
        
        except Exception as e:
            logger.error(f"Screenshot analysis failed: {e}")
            
            # 오류 상태 업데이트
            async with self.db.session() as session:
                screenshot.analysis_status = "FAILED"
                await self.screenshot_repo.update(screenshot, session=session)
                await session.commit()
            
            raise ScreenshotAnalysisError(f"Screenshot analysis failed: {str(e)}")
    
    async def get_screenshots(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Screenshot]:
        """
        사용자 스크린샷 목록 조회
        
        Args:
            user_id: 사용자 ID
            skip: 건너뛸 레코드 수
            limit: 최대 조회 레코드 수
        
        Returns:
            Screenshot 리스트
        """
        return await self.screenshot_repo.get_by_user_id(user_id, skip=skip, limit=limit)
    
    async def delete_screenshot(
        self,
        screenshot_id: int,
        user_id: int
    ) -> bool:
        """
        스크린샷 삭제
        
        Args:
            screenshot_id: 스크린샷 ID
            user_id: 사용자 ID
        
        Returns:
            삭제 성공 여부
        """
        # 스크린샷 조회 및 소유권 확인
        screenshot = await self.screenshot_repo.get_by_id(screenshot_id)
        if not screenshot:
            raise ValidationError(f"Screenshot not found: {screenshot_id}")
        
        if screenshot.user_id != user_id:
            raise ValidationError("본인의 스크린샷만 삭제할 수 있습니다.")
        
        # 파일 삭제
        try:
            if Path(screenshot.file_path).exists():
                Path(screenshot.file_path).unlink()
        except Exception as e:
            logger.warning(f"Failed to delete image file: {e}")
        
        # 데이터베이스에서 삭제
        result = await self.screenshot_repo.delete(screenshot_id)
        
        logger.info(f"Screenshot deleted: screenshot_id={screenshot_id}")
        return result

