"""
스케줄러 서비스 - 주기적으로 모니터링 실행
"""
import asyncio
from datetime import datetime, timedelta

from config.logging import get_logger
from src.services.portfolio_monitoring_service import PortfolioMonitoringService

logger = get_logger(__name__)


class SchedulerService:
    """백그라운드 작업 스케줄러"""
    
    def __init__(self):
        self.monitoring_service = PortfolioMonitoringService()
        self.running = False
    
    async def start(self):
        """스케줄러 시작"""
        self.running = True
        logger.info("Scheduler service started")
        
        # 여러 태스크를 병렬로 실행
        try:
            await asyncio.gather(
                self._daily_monitoring_loop(),
                self._weekly_review_loop(),
                self._monthly_goal_check_loop()
            )
        except asyncio.CancelledError:
            logger.info("Scheduler service cancelled")
        except Exception as e:
            logger.error(f"Scheduler service error: {e}", exc_info=True)
        finally:
            self.running = False
            logger.info("Scheduler service stopped")
    
    async def _daily_monitoring_loop(self):
        """매일 포트폴리오 모니터링"""
        while self.running:
            try:
                # 매일 오전 9시에 실행
                now = datetime.now()
                next_run = now.replace(hour=9, minute=0, second=0, microsecond=0)
                if next_run <= now:
                    next_run += timedelta(days=1)
                
                wait_seconds = (next_run - now).total_seconds()
                logger.info(f"Next daily monitoring scheduled at {next_run}")
                await asyncio.sleep(wait_seconds)
                
                if not self.running:
                    break
                
                logger.info("Starting daily portfolio monitoring")
                await self.monitoring_service.monitor_all_users()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in daily monitoring: {e}", exc_info=True)
                await asyncio.sleep(3600)  # 1시간 후 재시도
    
    async def _weekly_review_loop(self):
        """주간 리뷰"""
        while self.running:
            try:
                # 매주 월요일 오전 10시
                await asyncio.sleep(7 * 24 * 3600)  # 7일 대기
                
                if not self.running:
                    break
                
                if datetime.now().weekday() == 0:  # 월요일
                    logger.info("Starting weekly portfolio review")
                    # 주간 리포트 생성 등 (추후 구현)
                    await self.monitoring_service.monitor_all_users()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in weekly review: {e}", exc_info=True)
                await asyncio.sleep(3600)
    
    async def _monthly_goal_check_loop(self):
        """월간 목표 체크"""
        while self.running:
            try:
                # 매월 1일
                await asyncio.sleep(30 * 24 * 3600)  # 30일 대기
                
                if not self.running:
                    break
                
                if datetime.now().day == 1:
                    logger.info("Starting monthly goal check")
                    # 월간 목표 진행 상황 리포트 (추후 구현)
                    await self.monitoring_service.monitor_all_users()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monthly goal check: {e}", exc_info=True)
                await asyncio.sleep(3600)
    
    def stop(self):
        """스케줄러 중지"""
        self.running = False
        logger.info("Scheduler service stop requested")

