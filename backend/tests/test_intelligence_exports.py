def _create_threat(client, headers, indicator, indicator_type, source, severity="high"):
    response = client.post(
        "/api/threats/analyze",
        headers=headers,
        json={
            "indicator": indicator,
            "indicator_type": indicator_type,
            "threat_type": "suspicious_ip" if indicator_type == "ip" else "malware",
            "source": source,
            "severity": severity,
            "description": f"Observation {source}",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_stix_and_misp_exports(client, auth_headers):
    _create_threat(client, auth_headers, "203.0.113.77", "ip", "otx")

    stix = client.get("/api/intelligence/export/stix", headers=auth_headers)
    misp = client.get("/api/intelligence/export/misp", headers=auth_headers)

    assert stix.status_code == 200
    assert stix.json()["type"] == "bundle"
    indicator = next(item for item in stix.json()["objects"] if item["type"] == "indicator")
    assert indicator["spec_version"] == "2.1"
    assert "ipv4-addr:value" in indicator["pattern"]
    assert misp.status_code == 200
    assert misp.json()["Event"]["distribution"] == "0"
    assert any(
        item["type"] == "ip-dst" and item["value"] == "203.0.113.77"
        for item in misp.json()["Event"]["Attribute"]
    )


def test_taxii_read_only_collection(client, auth_headers):
    _create_threat(client, auth_headers, "taxii.example", "domain", "otx")

    discovery = client.get("/taxii2/")
    collections = client.get("/api/taxii2/collections/", headers=auth_headers)
    collection_id = collections.json()["collections"][0]["id"]
    objects = client.get(
        f"/api/taxii2/collections/{collection_id}/objects/", headers=auth_headers
    )

    assert discovery.status_code == 200
    assert discovery.json()["api_roots"] == ["/api/taxii2/"]
    assert collections.json()["collections"][0]["can_write"] is False
    assert objects.status_code == 200
    assert "application/taxii+json" in objects.headers["content-type"]
    assert any(item.get("name") == "taxii.example" for item in objects.json()["objects"])


def test_correlations_merge_sources_for_same_indicator(client, auth_headers):
    _create_threat(client, auth_headers, "shared.example", "domain", "otx")
    _create_threat(client, auth_headers, "shared.example", "domain", "urlhaus")

    response = client.get("/api/intelligence/correlations", headers=auth_headers)

    assert response.status_code == 200
    correlation = next(
        item for item in response.json() if item["indicator"] == "shared.example"
    )
    assert correlation["source_count"] == 2
    assert correlation["sources"] == ["otx", "urlhaus"]
    assert correlation["confidence"] >= 80


def test_anomaly_endpoint_is_explainable(client, auth_headers):
    for index in range(6):
        _create_threat(
            client,
            auth_headers,
            f"198.51.100.{index}",
            "ip",
            "manual",
            severity="low",
        )
    outlier = _create_threat(
        client, auth_headers, "198.51.100.250", "ip", "manual", severity="critical"
    )

    response = client.get("/api/intelligence/anomalies", headers=auth_headers)

    assert response.status_code == 200
    item = next(entry for entry in response.json() if entry["threat_id"] == outlier["id"])
    assert item["method"] == "median_mad"
    assert item["observed_score"] == outlier["risk_score"]
    assert item["reason"]
