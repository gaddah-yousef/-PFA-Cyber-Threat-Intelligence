def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_threats_require_auth(client):
    response = client.get("/api/threats")
    assert response.status_code == 401


def test_stats_require_auth_and_report_totals(client, auth_headers):
    assert client.get("/api/stats").status_code == 401

    response = client.get("/api/stats", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert set(body) == {"total", "critical", "high", "medium", "low", "alerts"}


def test_threat_analyze_endpoint(client, auth_headers):
    response = client.post(
        "/api/threats/analyze",
        headers=auth_headers,
        json={
            "indicator": "login-microsoft.example",
            "indicator_type": "domain",
            "threat_type": "phishing",
            "source": "otx",
            "severity": "high",
            "description": "Domaine de phishing ciblant une PME",
            "targets_smes": True,
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["risk_score"] >= 70
    assert body["risk_level"] in {"high", "critical"}
    assert "Bloquer" in body["recommended_action"]


def test_analyze_same_indicator_upserts_instead_of_duplicating(client, auth_headers):
    payload = {
        "indicator": "duplicate-domain.example",
        "indicator_type": "domain",
        "threat_type": "phishing",
        "source": "manual",
        "severity": "medium",
    }
    first = client.post("/api/threats/analyze", headers=auth_headers, json=payload)
    second = client.post(
        "/api/threats/analyze",
        headers=auth_headers,
        json={**payload, "severity": "critical"},
    )
    assert first.json()["id"] == second.json()["id"]
    assert second.json()["severity"] == "critical"

    listed = client.get(
        "/api/threats", headers=auth_headers, params={"search": "duplicate-domain"}
    )
    assert len(listed.json()) == 1


def test_viewer_cannot_write_threats(client, auth_headers):
    client.post(
        "/api/auth/users",
        headers=auth_headers,
        json={"email": "pme@example.com", "password": "SuperSecret1", "role": "viewer"},
    )
    login = client.post(
        "/api/auth/login", data={"username": "pme@example.com", "password": "SuperSecret1"}
    )
    viewer_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = client.post(
        "/api/threats/manual",
        headers=viewer_headers,
        json={"indicator": "1.2.3.4", "indicator_type": "ip", "threat_type": "brute_force"},
    )
    assert response.status_code == 403

    readable = client.get("/api/threats", headers=viewer_headers)
    assert readable.status_code == 200


def test_critical_threats_endpoint(client, auth_headers):
    response = client.get("/api/threats/critical", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()
    assert all(item["risk_score"] >= 90 for item in response.json())


def test_reflex_sheet_output(client, auth_headers):
    response = client.get("/api/reflex-sheets/phishing", headers=auth_headers)
    assert response.status_code == 200
    sheet = response.json()
    assert sheet["threat_type"] == "phishing"
    assert len(sheet["actions"]) >= 4
    assert sheet["priority"] in {"critique", "élevée", "modérée"}
    assert len(sheet["sections"]) >= 3
    assert all(section["timeframe"] and section["actions"] for section in sheet["sections"])
    assert sheet["evidence_to_preserve"]
    assert sheet["escalation_criteria"]
    assert sheet["references"]


def test_alert_acknowledge_flow(client, auth_headers):
    client.post(
        "/api/threats/manual",
        headers=auth_headers,
        json={
            "indicator": "ransom-crew.example",
            "indicator_type": "domain",
            "threat_type": "ransomware",
            "severity": "critical",
        },
    )
    alerts = client.get("/api/alerts", headers=auth_headers).json()
    assert alerts, "une alerte critique aurait dû être créée"
    alert_id = alerts[0]["id"]

    response = client.patch(f"/api/alerts/{alert_id}/acknowledge", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["acknowledged"] is True
    assert response.json()["status"] == "resolved"


def test_alert_soc_status_update_flow(client, auth_headers):
    client.post(
        "/api/threats/manual",
        headers=auth_headers,
        json={
            "indicator": "soc-workflow.example",
            "indicator_type": "domain",
            "threat_type": "phishing",
            "severity": "critical",
        },
    )
    alert = client.get("/api/alerts", headers=auth_headers).json()[0]

    response = client.patch(
        f"/api/alerts/{alert['id']}",
        headers=auth_headers,
        json={
            "status": "investigating",
            "assigned_to": "analyst@sentinel.local",
            "resolution_notes": "Analyse en cours côté SOC.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "investigating"
    assert body["assigned_to"] == "analyst@sentinel.local"
    assert body["resolution_notes"] == "Analyse en cours côté SOC."
    assert body["acknowledged"] is False


def test_alert_siem_event_export(client, auth_headers):
    created = client.post(
        "/api/threats/manual",
        headers=auth_headers,
        json={
            "indicator": "https://malware.example/payload.exe",
            "indicator_type": "url",
            "threat_type": "malware",
            "source": "manual",
            "severity": "critical",
            "description": "URL de distribution malware observée dans une campagne ciblant les PME.",
            "targets_smes": True,
        },
    )
    alerts = client.get("/api/alerts", headers=auth_headers).json()
    alert = next(item for item in alerts if item["threat_id"] == created.json()["id"])

    response = client.get(f"/api/alerts/{alert['id']}/siem-event", headers=auth_headers)

    assert response.status_code == 200
    event = response.json()
    assert event["schema_version"] == "1.0"
    assert event["event_type"] == "sentinel_pme.threat_alert"
    assert event["alert"]["id"] == alert["id"]
    assert event["alert"]["status"] == "new"
    assert event["threat"]["indicator"] == "https://malware.example/payload.exe"
    assert event["threat"]["risk_score"] >= 90
    assert event["recommended_action"]


def test_collectors_list_and_sample_run(client, auth_headers):
    listed = client.get("/api/collectors", headers=auth_headers)
    assert listed.status_code == 200
    names = {item["name"] for item in listed.json()}
    assert {"sample", "urlhaus", "nvd", "abuseipdb", "otx"}.issubset(names)

    response = client.post("/api/collectors/sample/run", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["threats_processed"] > 0


def test_collector_failure_does_not_expose_secret_in_api_error(
    client, auth_headers, monkeypatch
):
    from app.api import routes_collectors

    async def failing_collector(*_args, **_kwargs):
        raise RuntimeError("https://provider.example/private-secret-value/export")

    monkeypatch.setattr(routes_collectors, "run_collector", failing_collector)
    response = client.post("/api/collectors/urlhaus/run", headers=auth_headers)

    assert response.status_code == 502
    assert "private-secret-value" not in response.text
    assert "Vérifiez sa configuration" in response.json()["detail"]
