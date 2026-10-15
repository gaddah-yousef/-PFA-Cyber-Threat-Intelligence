from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.threat import Threat
from app.schemas.threat import ThreatInput
from app.services.alert_service import create_alert_for_threat
from app.services.reflex_sheets import get_recommended_action
from app.services.risk_scoring import calculate_risk


def count_corroborating_sources(db: Session, payload: ThreatInput) -> int:
    """Nombre de sources distinctes, autres que celle du payload, ayant déjà
    rapporté le même indicateur. Sert de bonus de confiance au scoring."""

    other_sources = db.scalars(
        select(Threat.source)
        .where(Threat.indicator == payload.indicator, Threat.source != payload.source.value)
        .distinct()
    ).all()
    return len(set(other_sources))


def analyze_and_save_threat(db: Session, payload: ThreatInput) -> Threat:
    """Analyse une menace et l'enregistre. Met à jour l'entrée existante (même
    indicateur + même source) au lieu d'en créer une nouvelle, afin qu'une
    collecte répétée ne duplique pas les menaces ni les alertes."""

    threat = db.scalar(
        select(Threat).where(
            Threat.indicator == payload.indicator,
            Threat.source == payload.source.value,
        )
    )

    effective_payload = payload
    if threat is not None:
        preserved: dict[str, object] = {}
        for field in ("epss_score", "epss_percentile", "epss_updated_at"):
            if getattr(payload, field) is None:
                preserved[field] = getattr(threat, field)
        if payload.known_exploited is None:
            preserved.update(
                {
                    "known_exploited": threat.known_exploited,
                    "kev_date_added": threat.kev_date_added,
                    "kev_due_date": threat.kev_due_date,
                    "kev_required_action": threat.kev_required_action,
                    "kev_ransomware_use": threat.kev_ransomware_use,
                }
            )
        if payload.targets_smes is None:
            preserved["targets_smes"] = threat.targets_smes
        if preserved:
            effective_payload = payload.model_copy(update=preserved)

    corroboration = count_corroborating_sources(db, effective_payload)
    score, level, factors = calculate_risk(
        effective_payload, corroborating_sources=corroboration
    )
    recommended_action = get_recommended_action(effective_payload.threat_type.value)

    if threat is None:
        threat = Threat(
            indicator=effective_payload.indicator,
            first_seen=effective_payload.first_seen,
        )
        db.add(threat)

    threat.indicator_type = effective_payload.indicator_type.value
    threat.threat_type = effective_payload.threat_type.value
    threat.source = effective_payload.source.value
    threat.severity = effective_payload.severity.value
    threat.risk_score = score
    threat.risk_level = level.value
    threat.score_factors = factors
    threat.cvss_score = effective_payload.cvss_score
    threat.cve_configurations = effective_payload.cve_configurations
    threat.epss_score = effective_payload.epss_score
    threat.epss_percentile = effective_payload.epss_percentile
    threat.epss_updated_at = effective_payload.epss_updated_at
    threat.known_exploited = bool(effective_payload.known_exploited)
    threat.targets_smes = bool(effective_payload.targets_smes)
    threat.kev_date_added = effective_payload.kev_date_added
    threat.kev_due_date = effective_payload.kev_due_date
    threat.kev_required_action = effective_payload.kev_required_action
    threat.kev_ransomware_use = effective_payload.kev_ransomware_use
    threat.description = effective_payload.description
    threat.recommended_action = recommended_action
    threat.last_seen = effective_payload.last_seen

    db.flush()
    create_alert_for_threat(db, threat)
    db.commit()
    db.refresh(threat)
    return threat
