"""Adaptateurs de sortie vers des formats SIEM courants."""

from datetime import datetime, timezone

from app.models.alert import Alert
from app.models.threat import Threat


def _iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


def build_elastic_ecs_event(alert: Alert, threat: Threat) -> dict:
    indicator: dict[str, object] = {
        "id": [threat.id],
        "type": threat.indicator_type,
        "description": threat.description,
        "first_seen": _iso(threat.first_seen),
        "last_seen": _iso(threat.last_seen),
    }
    field_by_type = {
        "ip": "ip",
        "domain": "url.domain",
        "url": "url.full",
        "hash": "file.hash.sha256",
        "cve": "vulnerability.id",
    }
    indicator[field_by_type.get(threat.indicator_type, "name")] = threat.indicator

    return {
        "@timestamp": datetime.now(timezone.utc).isoformat(),
        "ecs": {"version": "9.3.0"},
        "event": {
            "kind": "alert",
            "category": ["threat"],
            "type": ["indicator"],
            "module": "sentinel_pme",
            "action": "threat_alert",
            "severity": 90 if alert.level == "critical" else 70,
            "risk_score_norm": threat.risk_score,
        },
        "message": alert.message,
        "rule": {"id": alert.id, "name": alert.title},
        "threat": {"indicator": indicator},
        "labels": {
            "sentinel_status": alert.status,
            "sentinel_source": threat.source,
            "sentinel_risk_level": threat.risk_level,
        },
    }


def build_wazuh_event(alert: Alert, threat: Threat) -> dict:
    wazuh_level = {"critical": 15, "high": 12, "medium": 8, "low": 4}.get(
        alert.level, 5
    )
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "integration": "sentinel-pme",
        "rule": {
            "id": f"sentinel-{alert.id}",
            "level": wazuh_level,
            "description": alert.title,
        },
        "alert": {
            "id": alert.id,
            "status": alert.status,
            "assigned_to": alert.assigned_to,
            "message": alert.message,
        },
        "threat": {
            "id": threat.id,
            "indicator": threat.indicator,
            "indicator_type": threat.indicator_type,
            "type": threat.threat_type,
            "source": threat.source,
            "risk_score": threat.risk_score,
            "risk_level": threat.risk_level,
        },
    }
