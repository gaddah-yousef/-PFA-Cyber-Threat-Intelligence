"""Adaptateur RQ optionnel pour les collectes asynchrones."""

import asyncio

from app.core.config import settings
from app.database import SessionLocal
from app.services.collector_registry import COLLECTORS, run_collector


def run_collector_job(name: str, limit: int = 20) -> dict[str, object]:
    if name not in COLLECTORS:
        raise ValueError(f"Collecteur inconnu: {name}")
    with SessionLocal() as db:
        processed = asyncio.run(run_collector(db, name, limit=limit))
    return {"collector": name, "threats_processed": processed}


def _connection():
    if not settings.redis_url:
        raise RuntimeError("REDIS_URL n'est pas configurée")
    from redis import Redis

    return Redis.from_url(settings.redis_url)


def enqueue_collector(name: str, limit: int = 20) -> dict[str, object]:
    from rq import Queue

    job = Queue(settings.task_queue_name, connection=_connection()).enqueue(
        run_collector_job,
        name,
        limit,
        job_timeout=900,
        result_ttl=86400,
        failure_ttl=604800,
    )
    return {"job_id": job.id, "status": "queued", "collector": name}


def get_job_status(job_id: str) -> dict[str, object] | None:
    from rq.job import Job
    from rq.registry import FailedJobRegistry, FinishedJobRegistry, StartedJobRegistry

    connection = _connection()
    try:
        job = Job.fetch(job_id, connection=connection)
    except Exception as exc:  # RQ normalise différemment NoSuchJob selon la version
        if exc.__class__.__name__ == "NoSuchJobError":
            return None
        raise

    registries = {
        "started": StartedJobRegistry(settings.task_queue_name, connection=connection),
        "finished": FinishedJobRegistry(settings.task_queue_name, connection=connection),
        "failed": FailedJobRegistry(settings.task_queue_name, connection=connection),
    }
    status = job.get_status(refresh=True)
    for label, registry in registries.items():
        if job_id in registry:
            status = label
            break
    return {"job_id": job.id, "status": status, "result": job.result if status == "finished" else None}
