"""
백그라운드 워커 시작 스크립트
포트폴리오 모니터링 및 스케줄러 실행
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.logging import get_logger
from src.services.scheduler_service import SchedulerService

logger = get_logger(__name__)


async def main():
    """메인 함수"""
    logger.info("Starting background worker...")
    
    scheduler = SchedulerService()
    
    try:
        await scheduler.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, stopping...")
        scheduler.stop()
    except Exception as e:
        logger.error(f"Background worker error: {e}", exc_info=True)
        raise
    finally:
        logger.info("Background worker stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Background worker interrupted")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

