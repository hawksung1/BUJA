"""
BUJA 프로젝트 설정 모듈
"""
from config.logging import get_logger, setup_logging
from config.settings import Settings, settings

# 로깅 초기화
setup_logging(level=settings.log_level, log_file=settings.log_file)

__all__ = [
    "Settings",
    "settings",
    "setup_logging",
    "get_logger",
]

