import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.database import SessionLocal
from app.services.collector_registry import run_all_collectors

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()
HOURLY_COLLECTORS = ("sample", "urlhaus", "nvd", "otx")


async def scheduled_collection_job() -> None:
    with SessionLocal() as db:
        results = await run_all_collectors(db, names=HOURLY_COLLECTORS)
        logger.info("Collecte planifiée terminée: %s", results)


async def scheduled_abuseipdb_collection_job() -> None:
    with SessionLocal() as db:
        results = await run_all_collectors(db, names=("abuseipdb",))
        logger.info("Collecte AbuseIPDB terminée: %s", results)


def start_scheduler() -> None:
    if scheduler.running:
        return
    scheduler.add_job(
        scheduled_collection_job,
        "interval",
        minutes=settings.collector_interval_minutes,
        id="threat_collection",
        replace_existing=True,
        next_run_time=datetime.now(timezone.utc) + timedelta(seconds=30),
    )
    scheduler.add_job(
        scheduled_abuseipdb_collection_job,
        "interval",
        minutes=settings.abuseipdb_interval_minutes,
        id="abuseipdb_collection",
        replace_existing=True,
        next_run_time=datetime.now(timezone.utc) + timedelta(seconds=30),
    )
    scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
