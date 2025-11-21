"""
ScreenshotService 단위 테스트
"""
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest

from config.database import Database
from src.exceptions import ImageUploadError, InvalidImageFormatError
from src.models import Screenshot
from src.services.screenshot_service import ScreenshotService


@pytest.fixture
def mock_db():
    """Mock Database 인스턴스"""
    return MagicMock(spec=Database)


@pytest.fixture
def screenshot_service(mock_db):
    """ScreenshotService 인스턴스"""
    return ScreenshotService(database=mock_db)


class TestScreenshotService:
    """ScreenshotService 테스트"""

    def test_validate_image_success(self, screenshot_service):
        """이미지 검증 성공 테스트"""
        # Create a valid 1x1 PNG image using Pillow
        from io import BytesIO

        from PIL import Image

        img = Image.new('RGB', (1, 1), color='red')
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        png_data = img_byte_arr.getvalue()

        result = screenshot_service.validate_image(png_data)

        assert result["valid"] is True
        assert result["format"] == "PNG"

    def test_validate_image_too_large(self, screenshot_service):
        """이미지 크기 초과 테스트"""
        large_data = b"x" * (11 * 1024 * 1024)  # 11MB

        with pytest.raises(ImageUploadError):
            screenshot_service.validate_image(large_data, max_size=10 * 1024 * 1024)

    def test_validate_image_invalid_format(self, screenshot_service):
        """잘못된 이미지 형식 테스트"""
        invalid_data = b"not an image"

        with pytest.raises(InvalidImageFormatError):
            screenshot_service.validate_image(invalid_data)

    @pytest.mark.asyncio
    async def test_upload_screenshot(self, screenshot_service, mock_db):
        """스크린샷 업로드 테스트"""
        # Mock 설정
        mock_user_service = MagicMock()
        mock_user_service.get_user = AsyncMock()
        screenshot_service.user_service = mock_user_service

        mock_screenshot_repo = MagicMock()
        mock_screenshot_repo.create = AsyncMock(return_value=Screenshot(
            id=1, user_id=1, file_path="test.png", file_size=100, app_type="KEYUM"
        ))
        screenshot_service.screenshot_repo = mock_screenshot_repo

        mock_session = AsyncMock()
        mock_db.session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_db.session.return_value.__aexit__ = AsyncMock(return_value=None)
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        # Create a valid 1x1 PNG image using Pillow
        from io import BytesIO

        from PIL import Image

        img = Image.new('RGB', (1, 1), color='red')
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        png_data = img_byte_arr.getvalue()

        with patch("builtins.open", mock_open()), \
             patch("pathlib.Path.mkdir"):
            result = await screenshot_service.upload_screenshot(
                1, png_data, app_type="KEYUM"
            )

            assert result.user_id == 1
            assert result.app_type == "KEYUM"

