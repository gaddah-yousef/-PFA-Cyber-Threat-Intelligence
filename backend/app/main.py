from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import func, select, text

from app.api.routes_alerts import router as alerts_router
from app.api.routes_assets import router as assets_router
from app.api.routes_audit import router as audit_router
from app.api.routes_auth import router as auth_router
from app.api.routes_collectors import router as collectors_router
from app.api.routes_intelligence import router as intelligence_router
from app.api.routes_reflex import router as reflex_router
from app.api.routes_threats import router as threats_router
from app.api.routes_taxii import discovery_router as taxii_discovery_router
from app.api.routes_taxii import router as taxii_router
from app.collectors.sample_collector import SampleCollector
from app.core.config import settings
from app.core.deps import CurrentUser
from app.core.observability import configure_logging, metrics
from app.core.rate_limit import limiter
from app.core.security import hash_password
from app.database import SessionLocal, init_db
from app.models.alert import Alert
from app.models.threat import Threat
from app.models.user import User, UserRole
from app.services.scheduler import start_scheduler, stop_scheduler
from app.services.threat_service import analyze_and_save_threat

configure_logging(json_output=settings.environment != "development")


async def seed_database() -> None:
    with SessionLocal() as db:
        if (db.scalar(select(func.count(Threat.id))) or 0) == 0:
            for payload in await SampleCollector().collect():
                analyze_and_save_threat(db, payload)

        if (db.scalar(select(func.count(User.id))) or 0) == 0:
            admin = User(
                email=settings.admin_email,
                hashed_password=hash_password(settings.admin_password),
                role=UserRole.admin.value,
            )
            db.add(admin)
            db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    await seed_database()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title=settings.app_name,
    description="API de veille, détection et alerte précoce des cybermenaces ciblant les PME",
    version=settings.app_version,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    if settings.environment == "production":
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    return response


@app.middleware("http")
async def request_observability(request: Request, call_next):
    started = perf_counter()
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    try:
        response = await call_next(request)
    except Exception:
        metrics.observe(request.method, request.url.path, 500, perf_counter() - started)
        raise
    route = request.scope.get("route")
    path = getattr(route, "path", request.url.path)
    metrics.observe(request.method, path, response.status_code, perf_counter() - started)
    response.headers["X-Request-ID"] = request_id
    return response


app.include_router(auth_router)
app.include_router(assets_router)
app.include_router(threats_router)
app.include_router(alerts_router)
app.include_router(reflex_router)
app.include_router(collectors_router)
app.include_router(audit_router)
app.include_router(intelligence_router)
app.include_router(taxii_discovery_router)
app.include_router(taxii_router)


@app.get("/", tags=["System"])
def root() -> dict[str, str]:
    return {
        "message": settings.app_name,
        "status": "running",
        "documentation": "/docs",
    }


@app.get("/health", tags=["System"])
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}


@app.get("/health/ready", tags=["System"])
def readiness() -> dict:
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    return {"status": "ready", "checks": {"database": "ok"}}


@app.get("/metrics", tags=["System"], include_in_schema=False)
def prometheus_metrics() -> Response:
    return Response(content=metrics.render(), media_type="text/plain; version=0.0.4")


@app.get("/api/stats", tags=["Dashboard"])
def stats(_current_user: CurrentUser) -> dict[str, int]:
    with SessionLocal() as db:
        rows = dict(
            db.execute(select(Threat.risk_level, func.count(Threat.id)).group_by(Threat.risk_level)).all()
        )
        total = sum(rows.values())
        counts = {level: rows.get(level, 0) for level in ("critical", "high", "medium", "low")}
        alerts = db.scalar(select(func.count(Alert.id))) or 0
    return {"total": total, **counts, "alerts": alerts}
