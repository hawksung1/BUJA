"""
로깅 시스템 구축 (JSON 형식 구조화 로깅)
"""
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from config.settings import settings


class JSONFormatter(logging.Formatter):
    """JSON 형식 로거 포맷터"""

    def format(self, record: logging.LogRecord) -> str:
        """로그 레코드를 JSON 형식으로 변환"""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 예외 정보 추가
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # 추가 컨텍스트 정보
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id

        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        if hasattr(record, "extra_data"):
            log_data["extra"] = record.extra_data

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    로깅 시스템 설정
    
    Args:
        level: 로그 레벨 (기본값: settings.log_level)
        log_file: 로그 파일 경로 (기본값: settings.log_file)
    
    Returns:
        설정된 로거 인스턴스
    """
    log_level = level or settings.log_level
    log_file_path = log_file or settings.log_file

    # 루트 로거 설정
    logger = logging.getLogger("buja")
    logger.setLevel(getattr(logging, log_level))
    logger.handlers.clear()  # 기존 핸들러 제거

    # JSON 포맷터 생성
    json_formatter = JSONFormatter()

    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    console_handler.setLevel(getattr(logging, log_level))
    logger.addHandler(console_handler)

    # 파일 핸들러 (로그 파일이 지정된 경우)
    if log_file_path:
        log_path = Path(log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setFormatter(json_formatter)
        file_handler.setLevel(getattr(logging, log_level))
        logger.addHandler(file_handler)

    # 하위 로거도 동일한 레벨 사용
    logging.getLogger("buja").setLevel(getattr(logging, log_level))

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    로거 인스턴스 가져오기
    
    Args:
        name: 로거 이름 (일반적으로 __name__ 사용)
    
    Returns:
        로거 인스턴스
    """
    return logging.getLogger(f"buja.{name}")


# 전역 로거 초기화
setup_logging()

