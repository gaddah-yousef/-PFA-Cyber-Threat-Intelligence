from datetime import datetime, timezone

from app.schemas.threat import RiskLevel, ThreatInput


SEVERITY_POINTS = {"low": 5, "medium": 20, "high": 35, "critical": 50}
INDICATOR_POINTS = {"ip": 5, "domain": 7, "url": 8, "cve": 12, "hash": 6}
THREAT_POINTS = {
    "phishing": 10,
    "malware": 12,
    "ransomware": 18,
    "brute_force": 8,
    "vulnerability": 12,
    "suspicious_ip": 7,
    "unknown": 0,
}
SOURCE_POINTS = {
    "nvd": 12,
    "urlhaus": 11,
    "abuseipdb": 9,
    "otx": 9,
    "manual": 4,
    "sample": 4,
}


def risk_level_from_score(score: int) -> RiskLevel:
    if score >= 90:
        return RiskLevel.critical
    if score >= 70:
        return RiskLevel.high
    if score >= 40:
        return RiskLevel.medium
    return RiskLevel.low


def _recency_points(first_seen: datetime, now: datetime | None = None) -> int:
    now = now or datetime.now(timezone.utc)
    if first_seen.tzinfo is None:
        first_seen = first_seen.replace(tzinfo=timezone.utc)
    age_days = max((now - first_seen).days, 0)
    if age_days <= 7:
        return 8
    if age_days <= 30:
        return 5
    if age_days <= 90:
        return 2
    return 0


MAX_CORROBORATION_SOURCES = 2
CORROBORATION_POINTS_PER_SOURCE = 6


def calculate_risk(
    threat: ThreatInput, corroborating_sources: int = 0
) -> tuple[int, RiskLevel, dict[str, int]]:
    """Calcule un score explicable et borné entre 0 et 100.

    `corroborating_sources` est le nombre de sources distinctes, autres que
    la source courante, ayant déjà rapporté le même indicateur. Un indicateur
    vu par plusieurs sources de veille indépendantes est plus fiable : cela
    se traduit par un bonus de corrélation plafonné, pour éviter qu'un
    indicateur très collecté ne sature artificiellement le score.
    """

    indicator_type = threat.indicator_type.value
    threat_type = threat.threat_type.value
    source = threat.source.value
    severity = threat.severity.value

    epss_likelihood = 0
    if threat.epss_percentile is not None:
        if threat.epss_percentile >= 0.9:
            epss_likelihood = 10
        elif threat.epss_percentile >= 0.75:
            epss_likelihood = 5

    factors = {
        "severity": SEVERITY_POINTS[severity],
        "indicator_type": INDICATOR_POINTS[indicator_type],
        "threat_type": THREAT_POINTS[threat_type],
        "source_reliability": SOURCE_POINTS[source],
        "cve_bonus": 5 if indicator_type == "cve" else 0,
        "known_exploited": 15 if threat.known_exploited else 0,
        "epss_likelihood": epss_likelihood,
        "targets_smes": 10 if threat.targets_smes else 0,
        "recency": _recency_points(threat.first_seen),
        "multi_source_corroboration": (
            min(max(corroborating_sources, 0), MAX_CORROBORATION_SOURCES)
            * CORROBORATION_POINTS_PER_SOURCE
        ),
    }
    score = min(sum(factors.values()), 100)
    return score, risk_level_from_score(score), factors
