import asyncio
from datetime import datetime, timezone

import httpx
import pytest

from app.collectors.otx_collector import OTXCollector
from app.collectors.nvd_collector import NVDCollector
from app.collectors.urlhaus_collector import URLhausCollector
from app.core.config import Settings, settings
from app.services import scheduler as scheduler_module
from app.services import collector_registry as registry_module
from app.services import task_queue as task_queue_module
from app.schemas.threat import ThreatInput


def _nvd_entry(cve_id: str, published: str, score: float, metric: str = "cvssMetricV31"):
    return {
        "cve": {
            "id": cve_id,
            "published": published,
            "descriptions": [{"lang": "en", "value": f"Description for {cve_id}"}],
            "metrics": {metric: [{"cvssData": {"baseScore": score}}]},
        }
    }


def test_nvd_collector_fetches_the_last_recent_page_and_sorts_newest(monkeypatch):
    calls: list[dict] = []
    recent_entries = [
        _nvd_entry("CVE-2026-100001", "2026-10-06T20:00:00.000Z", 7.5),
        _nvd_entry("CVE-2026-100003", "2026-10-06T22:00:00.000Z", 9.3, "cvssMetricV40"),
        _nvd_entry("CVE-2026-100002", "2026-10-06T21:00:00.000Z", 5.5),
    ]

    class FakeResponse:
        def __init__(self, payload: dict):
            self.payload = payload

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return self.payload

    class FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def get(self, _url, *, params, headers):
            calls.append({"params": dict(params), "has_api_key": bool(headers)})
            if len(calls) == 1:
                return FakeResponse({"totalResults": 103, "vulnerabilities": []})
            return FakeResponse({"totalResults": 103, "vulnerabilities": recent_entries})

    monkeypatch.setattr(httpx, "AsyncClient", lambda **_kwargs: FakeAsyncClient())

    threats = asyncio.run(NVDCollector().collect(limit=3))

    assert len(calls) == 2
    first_params = calls[0]["params"]
    second_params = calls[1]["params"]
    assert "pubStartDate" in first_params
    assert "pubEndDate" in first_params
    assert datetime.fromisoformat(first_params["pubStartDate"]) < datetime.fromisoformat(
        first_params["pubEndDate"]
    )
    assert second_params["startIndex"] == 100
    assert [threat.indicator for threat in threats] == [
        "CVE-2026-100003",
        "CVE-2026-100002",
        "CVE-2026-100001",
    ]
    assert threats[0].severity.value == "critical"


def test_collector_settings_include_urlhaus_key_and_abuseipdb_interval():
    assert "urlhaus_auth_key" in Settings.model_fields
    assert Settings.model_fields["abuseipdb_interval_minutes"].default == 360


def test_urlhaus_collector_uses_authenticated_v2_csv_export(monkeypatch):
    calls: list[dict] = []

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        text = """################################################################
# abuse.ch URLhaus Database Dump (CSV - recent URLs only)
# id,dateadded,url,url_status,last_online,threat,tags,urlhaus_link,reporter
"1","2026-10-06 08:31:05 UTC","https://malware.example/payload.exe","online","2026-10-06","malware_download","exe","https://urlhaus.abuse.ch/url/1/","researcher"
"""

    class FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def get(self, url):
            calls.append({"url": url})
            return FakeResponse()

    monkeypatch.setattr(settings, "urlhaus_auth_key", "test-urlhaus-key", raising=False)
    monkeypatch.setattr(httpx, "AsyncClient", lambda **_kwargs: FakeAsyncClient())

    threats = asyncio.run(URLhausCollector().collect(limit=1))

    assert calls == [
        {"url": "https://urlhaus-api.abuse.ch/v2/files/exports/test-urlhaus-key/recent.csv"}
    ]
    assert threats[0].first_seen == datetime(2026, 10, 6, 8, 31, 5, tzinfo=timezone.utc)


def test_urlhaus_collector_rejects_missing_auth_key(monkeypatch):
    monkeypatch.setattr(settings, "urlhaus_auth_key", None, raising=False)

    with pytest.raises(ValueError, match="URLHAUS_AUTH_KEY"):
        asyncio.run(URLhausCollector().collect(limit=1))


def test_otx_collector_preserves_indicator_creation_date(monkeypatch):
    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "results": [
                    {
                        "name": "Recent pulse",
                        "created": "2026-10-05T08:00:00",
                        "indicators": [
                            {
                                "indicator": "malware.example",
                                "type": "domain",
                                "created": "2026-10-06T08:31:05",
                            }
                        ],
                    }
                ]
            }

    class FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def get(self, _url, *, params, headers):
            return FakeResponse()

    monkeypatch.setattr(settings, "otx_api_key", "test-otx-key")
    monkeypatch.setattr(httpx, "AsyncClient", lambda **_kwargs: FakeAsyncClient())

    threats = asyncio.run(OTXCollector().collect(limit=1))

    assert threats[0].first_seen == datetime(2026, 10, 6, 8, 31, 5, tzinfo=timezone.utc)


def test_scheduler_separates_abuseipdb_from_hourly_collectors(monkeypatch):
    scheduled_calls: list[tuple[str, ...] | None] = []

    class FakeSession:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

    async def fake_run_all_collectors(_db, limit=20, names=None):
        scheduled_calls.append(tuple(names) if names is not None else None)
        return {name: 1 for name in names or ()}

    monkeypatch.setattr(scheduler_module, "SessionLocal", FakeSession)
    monkeypatch.setattr(scheduler_module, "run_all_collectors", fake_run_all_collectors)

    asyncio.run(scheduler_module.scheduled_collection_job())
    asyncio.run(scheduler_module.scheduled_abuseipdb_collection_job())

    assert "abuseipdb" not in scheduled_calls[0]
    assert scheduled_calls[1] == ("abuseipdb",)


def test_scheduler_uses_a_separate_six_hour_abuseipdb_job(monkeypatch):
    jobs: list[dict] = []

    class FakeScheduler:
        running = False

        def add_job(self, function, trigger, **kwargs):
            jobs.append({"function": function, "trigger": trigger, **kwargs})

        def start(self):
            self.running = True

    fake_scheduler = FakeScheduler()
    monkeypatch.setattr(scheduler_module, "scheduler", fake_scheduler)
    monkeypatch.setattr(settings, "collector_interval_minutes", 60)
    monkeypatch.setattr(settings, "abuseipdb_interval_minutes", 360, raising=False)

    scheduler_module.start_scheduler()

    intervals = {job["id"]: job["minutes"] for job in jobs}
    assert intervals == {
        "threat_collection": 60,
        "abuseipdb_collection": 360,
    }


def test_nvd_registry_enriches_payloads_before_persistence(monkeypatch):
    original = ThreatInput(
        indicator="CVE-2026-30001",
        indicator_type="cve",
        threat_type="vulnerability",
        source="nvd",
        severity="high",
    )
    saved: list[ThreatInput] = []
    refreshed: list[object] = []

    class FakeCollector:
        async def collect(self, limit=20):
            assert limit == 1
            return [original]

    async def fake_enrich(payloads):
        return [payloads[0].model_copy(update={"known_exploited": True})]

    monkeypatch.setitem(registry_module.COLLECTORS, "nvd", FakeCollector())
    monkeypatch.setattr(registry_module, "enrich_threat_inputs", fake_enrich)
    monkeypatch.setattr(registry_module, "analyze_and_save_threat", lambda _db, item: saved.append(item))
    monkeypatch.setattr(
        registry_module,
        "refresh_all_asset_matches",
        lambda db: refreshed.append(db),
        raising=False,
    )

    fake_db = object()
    processed = asyncio.run(registry_module.run_collector(fake_db, "nvd", limit=1))

    assert processed == 1
    assert saved[0].known_exploited is True
    assert refreshed == [fake_db]


def test_collector_can_be_enqueued(client, auth_headers, monkeypatch):
    monkeypatch.setattr(settings, "redis_url", "redis://queue.test:6379/0")
    monkeypatch.setattr(
        task_queue_module,
        "enqueue_collector",
        lambda name, limit=20: {"job_id": "job-123", "status": "queued", "collector": name},
    )

    response = client.post("/api/collectors/sample/enqueue", headers=auth_headers)

    assert response.status_code == 202
    assert response.json() == {
        "job_id": "job-123",
        "status": "queued",
        "collector": "sample",
    }
