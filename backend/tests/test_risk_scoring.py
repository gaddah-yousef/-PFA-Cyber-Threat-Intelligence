from app.schemas.threat import ThreatInput
from app.services.risk_scoring import calculate_risk, risk_level_from_score


def test_risk_score_is_bounded_and_explained():
    threat = ThreatInput(
        indicator="CVE-2026-99999",
        indicator_type="cve",
        threat_type="vulnerability",
        source="nvd",
        severity="critical",
        known_exploited=True,
        targets_smes=True,
    )
    score, level, factors = calculate_risk(threat)
    assert score == 100
    assert level.value == "critical"
    assert factors["known_exploited"] == 15


def test_risk_level_thresholds():
    assert risk_level_from_score(39).value == "low"
    assert risk_level_from_score(40).value == "medium"
    assert risk_level_from_score(70).value == "high"
    assert risk_level_from_score(90).value == "critical"


def test_high_epss_percentile_increases_cve_priority():
    baseline = ThreatInput(
        indicator="CVE-2026-20001",
        indicator_type="cve",
        threat_type="vulnerability",
        source="nvd",
        severity="medium",
    )
    enriched = baseline.model_copy(update={"epss_score": 0.08, "epss_percentile": 0.92})

    baseline_score, _, _ = calculate_risk(baseline)
    enriched_score, _, factors = calculate_risk(enriched)

    assert enriched_score == baseline_score + 10
    assert factors["epss_likelihood"] == 10
