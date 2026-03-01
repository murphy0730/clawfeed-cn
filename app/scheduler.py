"""APScheduler integration — runs digest pipeline on cron schedules."""

from __future__ import annotations

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import get_settings
from app.services.digest_pipeline import run_pipeline

logger = logging.getLogger(__name__)

_scheduler: AsyncIOScheduler | None = None


def _parse_cron(expr: str) -> dict:
    """Parse a 4-field cron expression: minute hour day_of_week day_of_month."""
    parts = expr.strip().split()
    if len(parts) == 4:
        return {
            "minute": parts[0],
            "hour": parts[1],
            "day_of_week": parts[2],
            "day": parts[3],
        }
    # fallback: treat as standard 5-field cron (min hour dom month dow)
    if len(parts) >= 5:
        return {
            "minute": parts[0],
            "hour": parts[1],
            "day": parts[2],
            "month": parts[3],
            "day_of_week": parts[4],
        }
    raise ValueError(f"Invalid cron expression: {expr}")


async def _run_job(digest_type: str) -> None:
    logger.info("Scheduler triggered: %s", digest_type)
    try:
        result = await run_pipeline(digest_type)
        if result:
            logger.info("Scheduler completed: %s → digest #%d", digest_type, result)
        else:
            logger.info("Scheduler completed: %s → no digest generated", digest_type)
    except Exception:
        logger.exception("Scheduler job failed: %s", digest_type)


def start_scheduler() -> None:
    global _scheduler
    settings = get_settings()

    if not settings.scheduler_enabled:
        logger.info("Scheduler disabled (SCHEDULER_ENABLED=false)")
        return

    _scheduler = AsyncIOScheduler()

    jobs = [
        ("4h", settings.schedule_4h),
        ("daily", settings.schedule_daily),
        ("weekly", settings.schedule_weekly),
        ("monthly", settings.schedule_monthly),
    ]

    for digest_type, cron_expr in jobs:
        try:
            cron_kwargs = _parse_cron(cron_expr)
            _scheduler.add_job(
                _run_job,
                CronTrigger(**cron_kwargs),
                args=[digest_type],
                id=f"digest_{digest_type}",
                name=f"Generate {digest_type} digest",
                replace_existing=True,
            )
            logger.info("Scheduled %s digest: %s", digest_type, cron_expr)
        except Exception:
            logger.exception("Failed to schedule %s with cron=%s", digest_type, cron_expr)

    _scheduler.start()
    logger.info("Scheduler started with %d jobs", len(_scheduler.get_jobs()))


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
        _scheduler = None
