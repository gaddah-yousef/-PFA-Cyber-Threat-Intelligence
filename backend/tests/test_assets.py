import io
from datetime import datetime, timezone

from app.database import SessionLocal
from app.models.threat import Threat


def create_user_headers(client, auth_headers, email: str, role: str) -> dict[str, str]:
    created = client.post(
        "/api/auth/users",
        headers=auth_headers,
        json={"email": email, "password": "SuperSecret1", "role": role},
    )
    assert created.status_code == 201
    login = client.post(
        "/api/auth/login",
        data={"username": email, "password": "SuperSecret1"},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def valid_asset(**overrides) -> dict:
    payload = {
        "hostname": "srv-web-01",
        "ip_address": "192.0.2.10",
        "asset_type": "server",
        "operating_system": "Ubuntu Server 24.04",
        "environment": "production",
        "criticality": "critical",
        "internet_exposed": True,
        "owner": "Equipe infrastructure",
        "description": "Serveur web public",
    }
    return {**payload, **overrides}


def insert_cve(indicator: str, configurations: list[dict]) -> str:
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        threat = Threat(
            indicator=indicator,
            indicator_type="cve",
            threat_type="vulnerability",
            source="nvd",
            severity="high",
            risk_score=84,
            risk_level="high",
            description="Vulnérabilité de test avec configuration NVD structurée.",
            recommended_action="Appliquer le correctif de sécurité.",
            score_factors={"severity": 35},
            cve_configurations=configurations,
            cvss_score=8.8,
            first_seen=now,
            last_seen=now,
        )
        db.add(threat)
        db.commit()
        return threat.id


def test_asset_crud_validates_ip_and_supports_filters(client, auth_headers):
    invalid = client.post(
        "/api/assets",
        headers=auth_headers,
        json=valid_asset(ip_address="999.10.10.10"),
    )
    assert invalid.status_code == 422

    created = client.post("/api/assets", headers=auth_headers, json=valid_asset())
    assert created.status_code == 201
    body = created.json()
    assert body["ip_address"] == "192.0.2.10"
    assert body["software_count"] == 0
    asset_id = body["id"]

    listed = client.get(
        "/api/assets",
        headers=auth_headers,
        params={"search": "web-01", "criticality": "critical", "limit": 10},
    )
    assert listed.status_code == 200
    assert listed.headers["x-total-count"] == "1"
    assert [asset["id"] for asset in listed.json()] == [asset_id]

    updated = client.patch(
        f"/api/assets/{asset_id}",
        headers=auth_headers,
        json={"owner": "SOC", "internet_exposed": False},
    )
    assert updated.status_code == 200
    assert updated.json()["owner"] == "SOC"
    assert updated.json()["internet_exposed"] is False

    null_required = client.patch(
        f"/api/assets/{asset_id}", headers=auth_headers, json={"criticality": None}
    )
    assert null_required.status_code == 422

    assert client.get(f"/api/assets/{asset_id}", headers=auth_headers).status_code == 200
    assert client.delete(f"/api/assets/{asset_id}", headers=auth_headers).status_code == 204
    assert client.get(f"/api/assets/{asset_id}", headers=auth_headers).status_code == 404


def test_asset_rbac_is_enforced_by_api(client, auth_headers):
    viewer_headers = create_user_headers(client, auth_headers, "viewer-assets@test.local", "viewer")
    analyst_headers = create_user_headers(client, auth_headers, "analyst-assets@test.local", "analyst")

    assert client.get("/api/assets", headers=viewer_headers).status_code == 200
    assert (
        client.post("/api/assets", headers=viewer_headers, json=valid_asset()).status_code
        == 403
    )
    assert (
        client.post(
            "/api/assets",
            headers=analyst_headers,
            json=valid_asset(hostname="srv-analyst-01", ip_address="2001:db8::10"),
        ).status_code
        == 201
    )


def test_software_inventory_and_confirmed_version_range_matching(client, auth_headers):
    asset = client.post("/api/assets", headers=auth_headers, json=valid_asset()).json()
    software = client.post(
        f"/api/assets/{asset['id']}/software",
        headers=auth_headers,
        json={
            "name": "Widget Server",
            "vendor": "Acme",
            "version": "2.5.0",
            "cpe": "cpe:2.3:a:acme:widget_server:2.5.0:*:*:*:*:*:*:*",
            "purl": "pkg:generic/acme/widget-server@2.5.0",
        },
    )
    assert software.status_code == 201
    assert software.json()["asset_id"] == asset["id"]

    insert_cve(
        "CVE-2026-10001",
        [
            {
                "nodes": [
                    {
                        "operator": "OR",
                        "negate": False,
                        "cpeMatch": [
                            {
                                "vulnerable": True,
                                "criteria": "cpe:2.3:a:acme:widget_server:*:*:*:*:*:*:*:*",
                                "versionStartIncluding": "2.0.0",
                                "versionEndExcluding": "3.0.0",
                            }
                        ],
                    }
                ]
            }
        ],
    )

    response = client.get(
        f"/api/assets/{asset['id']}/vulnerabilities", headers=auth_headers
    )
    assert response.status_code == 200
    matches = response.json()
    match = next(item for item in matches if item["cve_id"] == "CVE-2026-10001")
    assert match["matching_status"] == "confirmed"
    assert match["software_name"] == "Widget Server"
    assert match["matching_evidence"]["version_in_range"] is True


def test_matching_is_potential_without_cpe_and_not_affected_outside_range(
    client, auth_headers
):
    asset = client.post("/api/assets", headers=auth_headers, json=valid_asset()).json()
    client.post(
        f"/api/assets/{asset['id']}/software",
        headers=auth_headers,
        json={"name": "Widget Server", "vendor": "Acme", "version": "4.0.0"},
    )
    client.post(
        f"/api/assets/{asset['id']}/software",
        headers=auth_headers,
        json={
            "name": "Widget Server",
            "vendor": "Acme",
            "version": "4.0.0",
            "cpe": "cpe:2.3:a:acme:widget_server:4.0.0:*:*:*:*:*:*:*",
        },
    )
    insert_cve(
        "CVE-2026-10002",
        [
            {
                "nodes": [
                    {
                        "operator": "OR",
                        "cpeMatch": [
                            {
                                "vulnerable": True,
                                "criteria": "cpe:2.3:a:acme:widget_server:*:*:*:*:*:*:*:*",
                                "versionEndIncluding": "3.0.0",
                            }
                        ],
                    }
                ]
            }
        ],
    )

    matches = client.get(
        f"/api/assets/{asset['id']}/vulnerabilities", headers=auth_headers
    ).json()
    statuses = {item["matching_status"] for item in matches if item["cve_id"] == "CVE-2026-10002"}
    assert statuses == {"potential", "not_affected"}


def test_complex_nvd_configuration_is_not_reported_as_confirmed(client, auth_headers):
    asset = client.post("/api/assets", headers=auth_headers, json=valid_asset()).json()
    client.post(
        f"/api/assets/{asset['id']}/software",
        headers=auth_headers,
        json={
            "name": "Widget Server",
            "vendor": "Acme",
            "version": "2.5.0",
            "cpe": "cpe:2.3:a:acme:widget_server:2.5.0:*:*:*:*:*:*:*",
        },
    )
    insert_cve(
        "CVE-2026-10003",
        [
            {
                "nodes": [
                    {
                        "operator": "AND",
                        "cpeMatch": [
                            {
                                "vulnerable": True,
                                "criteria": "cpe:2.3:a:acme:widget_server:*:*:*:*:*:*:*:*",
                            },
                            {
                                "vulnerable": False,
                                "criteria": "cpe:2.3:o:acme:appliance_os:*:*:*:*:*:*:*:*",
                            },
                        ],
                    }
                ]
            }
        ],
    )

    matches = client.get(
        f"/api/assets/{asset['id']}/vulnerabilities", headers=auth_headers
    ).json()
    match = next(item for item in matches if item["cve_id"] == "CVE-2026-10003")
    assert match["matching_status"] == "potential"
    assert "configuration" in match["matching_reason"].lower()


def test_asset_csv_import_reports_row_errors_and_skips_duplicates(client, auth_headers):
    csv_data = """hostname,ip_address,asset_type,operating_system,environment,criticality,internet_exposed,owner,description
srv-import-01,192.0.2.20,server,Debian 13,production,high,true,IT,Serveur importé
srv-import-02,not-an-ip,workstation,Windows 11,development,medium,false,IT,IP invalide
srv-import-01,192.0.2.21,server,Debian 13,production,high,true,IT,Doublon
"""
    response = client.post(
        "/api/assets/import",
        headers=auth_headers,
        files={"file": ("assets.csv", io.BytesIO(csv_data.encode("utf-8")), "text/csv")},
    )
    assert response.status_code == 200
    report = response.json()
    assert report["created"] == 1
    assert report["skipped"] == 1
    assert report["error_count"] == 1
    assert report["errors"][0]["row"] == 3


def test_asset_actions_are_audited(client, auth_headers):
    asset = client.post("/api/assets", headers=auth_headers, json=valid_asset()).json()
    client.patch(
        f"/api/assets/{asset['id']}", headers=auth_headers, json={"owner": "SOC"}
    )
    client.post(
        f"/api/assets/{asset['id']}/software",
        headers=auth_headers,
        json={"name": "Nginx", "vendor": "F5", "version": "1.26.0"},
    )

    logs = client.get("/api/audit-logs", headers=auth_headers).json()
    actions = {entry["action"] for entry in logs}
    assert {"asset.create", "asset.update", "software.create"}.issubset(actions)
