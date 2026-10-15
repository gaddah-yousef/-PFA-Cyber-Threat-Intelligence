"""Tests pour les évolutions SOC/SIEM : scoring explicable, corrélation
multi-sources, journal d'audit et notification webhook."""

import httpx

from app.core.config import settings


def test_threat_explain_endpoint_exposes_score_factors(client, auth_headers):
    created = client.post(
        "/api/threats/manual",
        headers=auth_headers,
        json={
            "indicator": "CVE-2026-12345",
            "indicator_type": "cve",
            "threat_type": "vulnerability",
            "severity": "critical",
            "known_exploited": True,
            "targets_smes": True,
            "epss_score": 0.72,
            "epss_percentile": 0.98,
            "epss_updated_at": "2026-10-10T00:00:00Z",
            "kev_date_added": "2026-10-09",
            "kev_due_date": "2026-10-30",
            "kev_required_action": "Apply mitigations.",
            "kev_ransomware_use": "Known",
        },
    ).json()

    response = client.get(f"/api/threats/{created['id']}/explain", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["score"] == created["risk_score"]
    assert body["level"] == created["risk_level"]
    assert body["factors"]["known_exploited"] == 15
    assert body["factors"]["targets_smes"] == 10
    assert body["factors"]["epss_likelihood"] == 10
    assert "multi_source_corroboration" in body["factors"]

    details = client.get(f"/api/threats/{created['id']}", headers=auth_headers).json()
    assert details["epss_score"] == 0.72
    assert details["epss_percentile"] == 0.98
    assert details["known_exploited"] is True
    assert details["kev_due_date"] == "2026-10-30"
    assert details["kev_required_action"] == "Apply mitigations."


def test_explain_unknown_threat_returns_404(client, auth_headers):
    response = client.get("/api/threats/does-not-exist/explain", headers=auth_headers)
    assert response.status_code == 404


def test_multi_source_corroboration_increases_score(client, auth_headers):
    shared_indicator = "203.0.113.42"
    first = client.post(
        "/api/threats/analyze",
        headers=auth_headers,
        json={
            "indicator": shared_indicator,
            "indicator_type": "ip",
            "threat_type": "suspicious_ip",
            "source": "abuseipdb",
            "severity": "medium",
        },
    ).json()
    first_explained = client.get(f"/api/threats/{first['id']}/explain", headers=auth_headers).json()
    assert first_explained["factors"]["multi_source_corroboration"] == 0

    second = client.post(
        "/api/threats/analyze",
        headers=auth_headers,
        json={
            "indicator": shared_indicator,
            "indicator_type": "ip",
            "threat_type": "suspicious_ip",
            "source": "otx",
            "severity": "medium",
        },
    ).json()

    explained = client.get(f"/api/threats/{second['id']}/explain", headers=auth_headers).json()
    assert explained["factors"]["multi_source_corroboration"] == 6
    assert second["risk_score"] > first["risk_score"]


def test_nvd_refresh_does_not_erase_enrichment_when_sources_are_unavailable(
    client, auth_headers
):
    payload = {
        "indicator": "CVE-2026-19999",
        "indicator_type": "cve",
        "threat_type": "vulnerability",
        "source": "nvd",
        "severity": "high",
        "known_exploited": True,
        "epss_score": 0.55,
        "epss_percentile": 0.96,
        "kev_required_action": "Apply the vendor update.",
    }
    first = client.post("/api/threats/analyze", headers=auth_headers, json=payload)
    assert first.status_code == 201

    refresh = client.post(
        "/api/threats/analyze",
        headers=auth_headers,
        json={key: value for key, value in payload.items() if key not in {
            "known_exploited", "epss_score", "epss_percentile", "kev_required_action"
        }},
    )

    assert refresh.status_code == 201
    body = refresh.json()
    assert body["known_exploited"] is True
    assert body["epss_score"] == 0.55
    assert body["kev_required_action"] == "Apply the vendor update."


def test_targets_smes_is_persisted_and_preserved_on_refresh(client, auth_headers):
    payload = {
        "indicator": "CVE-2026-28888",
        "indicator_type": "cve",
        "threat_type": "vulnerability",
        "source": "nvd",
        "severity": "medium",
        "targets_smes": True,
    }
    created = client.post("/api/threats/analyze", headers=auth_headers, json=payload)
    assert created.status_code == 201
    assert created.json()["targets_smes"] is True

    payload.pop("targets_smes")
    refreshed = client.post("/api/threats/analyze", headers=auth_headers, json=payload)

    assert refreshed.status_code == 201
    assert refreshed.json()["targets_smes"] is True
    explained = client.get(
        f"/api/threats/{refreshed.json()['id']}/explain", headers=auth_headers
    ).json()
    assert explained["factors"]["targets_smes"] == 10


def test_audit_log_records_login_and_requires_admin(client, auth_headers):
    client.post(
        "/api/auth/users",
        headers=auth_headers,
        json={"email": "analyst@sentinel.local", "password": "SuperSecret1", "role": "analyst"},
    )

    response = client.get("/api/audit-logs", headers=auth_headers)
    assert response.status_code == 200
    actions = {entry["action"] for entry in response.json()}
    assert "auth.login" in actions
    assert "auth.create_user" in actions

    login = client.post(
        "/api/auth/login", data={"username": "analyst@sentinel.local", "password": "SuperSecret1"}
    )
    analyst_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    forbidden = client.get("/api/audit-logs", headers=analyst_headers)
    assert forbidden.status_code == 403


def test_alert_status_change_is_audited(client, auth_headers):
    client.post(
        "/api/threats/manual",
        headers=auth_headers,
        json={
            "indicator": "audit-flow.example",
            "indicator_type": "domain",
            "threat_type": "phishing",
            "severity": "critical",
        },
    )
    alert = client.get("/api/alerts", headers=auth_headers).json()[0]
    client.patch(
        f"/api/alerts/{alert['id']}",
        headers=auth_headers,
        json={"status": "investigating"},
    )

    logs = client.get("/api/audit-logs", headers=auth_headers).json()
    assert any(entry["action"] == "alert.update" and entry["target_id"] == alert["id"] for entry in logs)


def test_siem_event_requires_an_associated_threat(client, auth_headers):
    created = client.post("/api/alerts/test", headers=auth_headers, json={}).json()
    response = client.get(f"/api/alerts/{created['id']}/siem-event", headers=auth_headers)
    assert response.status_code == 404


def test_siem_vendor_formats_are_available(client, auth_headers):
    threat = client.post(
        "/api/threats/manual",
        headers=auth_headers,
        json={
            "indicator": "198.51.100.44",
            "indicator_type": "ip",
            "threat_type": "suspicious_ip",
            "source": "abuseipdb",
            "severity": "critical",
        },
    ).json()
    alert = next(
        item
        for item in client.get("/api/alerts", headers=auth_headers).json()
        if item["threat_id"] == threat["id"]
    )

    elastic = client.get(
        f"/api/alerts/{alert['id']}/siem-event/elastic", headers=auth_headers
    )
    wazuh = client.get(
        f"/api/alerts/{alert['id']}/siem-event/wazuh", headers=auth_headers
    )

    assert elastic.status_code == 200
    assert elastic.json()["ecs"]["version"] == "9.3.0"
    assert elastic.json()["threat"]["indicator"]["ip"] == "198.51.100.44"
    assert elastic.json()["event"]["risk_score_norm"] == threat["risk_score"]
    assert wazuh.status_code == 200
    assert wazuh.json()["integration"] == "sentinel-pme"
    assert wazuh.json()["rule"]["level"] == (
        15 if alert["level"] == "critical" else 12
    )
    assert wazuh.json()["threat"]["indicator"] == "198.51.100.44"


def test_webhook_is_dispatched_on_new_critical_alert(client, auth_headers, monkeypatch):
    calls: list[dict] = []

    def fake_post(url, content=None, headers=None, timeout=None):
        calls.append({"url": url, "content": content, "headers": headers})

        class _Resp:
            def raise_for_status(self) -> None:
                return None

        return _Resp()

    monkeypatch.setattr(settings, "webhook_url", "https://example.test/soc-webhook")
    monkeypatch.setattr(settings, "webhook_secret", "s3cret")
    monkeypatch.setattr(httpx, "post", fake_post)

    client.post(
        "/api/threats/manual",
        headers=auth_headers,
        json={
            "indicator": "webhook-test.example",
            "indicator_type": "domain",
            "threat_type": "ransomware",
            "severity": "critical",
        },
    )

    assert len(calls) == 1
    assert calls[0]["url"] == "https://example.test/soc-webhook"
    assert "X-Sentinel-Signature" in calls[0]["headers"]


def test_no_webhook_call_when_not_configured(client, auth_headers, monkeypatch):
    calls: list[dict] = []
    monkeypatch.setattr(httpx, "post", lambda *a, **k: calls.append(1))
    assert settings.webhook_url is None

    client.post(
        "/api/threats/manual",
        headers=auth_headers,
        json={
            "indicator": "no-webhook.example",
            "indicator_type": "domain",
            "threat_type": "malware",
            "severity": "critical",
        },
    )

    assert calls == []
