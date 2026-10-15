from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import CurrentUser, require_roles
from app.core.rate_limit import limiter
from app.database import get_db
from app.models.threat import Threat
from app.models.user import UserRole
from app.services.audit_log_service import record_audit_log
from app.services.collector_registry import COLLECTORS, run_collector
from app.services import task_queue

router = APIRouter(prefix="/api/collectors", tags=["Collecteurs"])
DbSession = Annotated[Session, Depends(get_db)]
CanRun = Depends(require_roles(UserRole.admin, UserRole.analyst))

REQUIRES_KEY = {
    "sample": None,
    "urlhaus": "urlhaus_auth_key",
    "nvd": "nvd_api_key",
    "abuseipdb": "abuseipdb_api_key",
    "otx": "otx_api_key",
}


@router.get("")
def list_collectors(db: DbSession, _current_user: CurrentUser) -> list[dict[str, object]]:
    counts = dict(
        db.execute(select(Threat.source, func.count(Threat.id)).group_by(Threat.source)).all()
    )
    last_seen = dict(
        db.execute(select(Threat.source, func.max(Threat.last_seen)).group_by(Threat.source)).all()
    )
    result = []
    for name in COLLECTORS:
        key_field = REQUIRES_KEY.get(name)
        configured = key_field is None or bool(getattr(settings, key_field))
        result.append(
            {
                "name": name,
                "requires_api_key": key_field is not None,
                "configured": configured,
                "threat_count": counts.get(name, 0),
                "last_collected_at": last_seen.get(name),
            }
        )
    return result


@router.post("/{name}/enqueue", status_code=status.HTTP_202_ACCEPTED, dependencies=[CanRun])
def enqueue_collector(
    name: str, db: DbSession, current_user: CurrentUser
) -> dict[str, object]:
    if name not in COLLECTORS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collecteur inconnu")
    if not settings.redis_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="File de tâches désactivée : configurez REDIS_URL",
        )
    try:
        result = task_queue.enqueue_collector(name)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La file de tâches est indisponible",
        ) from exc
    record_audit_log(
        db,
        current_user,
        action="collector.enqueue",
        target_type="collector",
        target_id=name,
        details=f"job_id={result['job_id']}",
    )
    return result


@router.get("/jobs/{job_id}")
def job_status(job_id: str, _current_user: CurrentUser) -> dict[str, object]:
    if not settings.redis_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="File de tâches désactivée : configurez REDIS_URL",
        )
    result = task_queue.get_job_status(job_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tâche introuvable")
    return result


@router.post("/{name}/run", dependencies=[CanRun])
@limiter.limit("6/minute")
async def trigger_collector(
    request: Request, name: str, db: DbSession, current_user: CurrentUser
) -> dict[str, object]:
    if name not in COLLECTORS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collecteur inconnu")
    try:
        processed = await run_collector(db, name)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"La source '{name}' n'a pas pu être interrogée. Vérifiez sa configuration.",
        ) from exc
    record_audit_log(
        db,
        current_user,
        action="collector.run",
        target_type="collector",
        target_id=name,
        details=f"threats_processed={processed}",
    )
    return {"source": name, "threats_processed": processed}
