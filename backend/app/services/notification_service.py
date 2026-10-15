"""Notifications SOC optionnelles, indépendantes et non bloquantes."""

import hashlib
import hmac
import json
import logging
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage

import httpx

from app.core.config import settings
from app.models.alert import Alert
from app.models.threat import Threat
from app.services.siem_service import build_elastic_ecs_event, build_wazuh_event

logger = logging.getLogger(__name__)

SIGNATURE_HEADER = "X-Sentinel-Signature"


def _sign(body: bytes) -> str | None:
    if not settings.webhook_secret:
        return None
    return hmac.new(settings.webhook_secret.encode("utf-8"), body, hashlib.sha256).hexdigest()


def build_webhook_payload(alert: Alert, threat: Threat | None) -> dict:
    return {
        "event_type": "sentinel_pme.alert_created",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "alert": {
            "id": alert.id,
            "level": alert.level,
            "status": alert.status,
            "title": alert.title,
            "message": alert.message,
        },
        "threat": (
            {
                "indicator": threat.indicator,
                "indicator_type": threat.indicator_type,
                "threat_type": threat.threat_type,
                "risk_score": threat.risk_score,
                "risk_level": threat.risk_level,
            }
            if threat is not None
            else None
        ),
    }


def send_alert_webhook(alert: Alert, threat: Threat | None) -> bool:
    """Envoie l'alerte au webhook SOC configuré. Renvoie False si aucun
    webhook n'est configuré ou si l'envoi a échoué (jamais d'exception)."""

    if not settings.webhook_url:
        return False

    body = json.dumps(build_webhook_payload(alert, threat), default=str).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    signature = _sign(body)
    if signature:
        headers[SIGNATURE_HEADER] = signature

    try:
        response = httpx.post(
            settings.webhook_url,
            content=body,
            headers=headers,
            timeout=settings.webhook_timeout_seconds,
        )
        response.raise_for_status()
        return True
    except httpx.HTTPError:
        logger.exception("Échec de l'envoi du webhook SOC pour l'alerte %s", alert.id)
        return False


def _message_text(alert: Alert, threat: Threat | None) -> str:
    indicator = threat.indicator if threat is not None else "sans indicateur associé"
    score = f" — score {threat.risk_score}/100" if threat is not None else ""
    return f"[{alert.level.upper()}] {alert.title}: {indicator}{score}. {alert.message}"


def send_slack_notification(alert: Alert, threat: Threat | None) -> bool:
    if not settings.slack_webhook_url:
        return False
    try:
        response = httpx.post(
            settings.slack_webhook_url,
            json={"text": _message_text(alert, threat)},
            timeout=settings.webhook_timeout_seconds,
        )
        response.raise_for_status()
        return True
    except httpx.HTTPError:
        logger.exception("Échec de la notification Slack pour l'alerte %s", alert.id)
        return False


def send_telegram_notification(alert: Alert, threat: Threat | None) -> bool:
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return False
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    try:
        response = httpx.post(
            url,
            json={"chat_id": settings.telegram_chat_id, "text": _message_text(alert, threat)},
            timeout=settings.webhook_timeout_seconds,
        )
        response.raise_for_status()
        return True
    except httpx.HTTPError:
        # Ne jamais journaliser l'URL : elle contient le jeton du bot.
        logger.exception("Échec de la notification Telegram pour l'alerte %s", alert.id)
        return False


def send_email_notification(alert: Alert, threat: Threat | None) -> bool:
    if not settings.smtp_host or not settings.smtp_from or not settings.alert_email_to:
        return False

    message = EmailMessage()
    message["Subject"] = f"[Sentinel PME] Alerte {alert.level.upper()}"
    message["From"] = settings.smtp_from
    message["To"] = ", ".join(settings.alert_email_to)
    message.set_content(_message_text(alert, threat))

    try:
        with smtplib.SMTP(
            settings.smtp_host,
            settings.smtp_port,
            timeout=settings.webhook_timeout_seconds,
        ) as smtp:
            if settings.smtp_starttls:
                smtp.starttls(context=ssl.create_default_context())
            if settings.smtp_username and settings.smtp_password:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)
        return True
    except (OSError, smtplib.SMTPException):
        logger.exception("Échec de la notification email pour l'alerte %s", alert.id)
        return False


def _send_siem_event(
    *, channel: str, url: str, payload: dict, authorization: str | None
) -> bool:
    headers = {"Content-Type": "application/json"}
    if authorization:
        headers["Authorization"] = authorization
    try:
        response = httpx.post(
            url,
            json=payload,
            headers=headers,
            timeout=settings.webhook_timeout_seconds,
        )
        response.raise_for_status()
        return True
    except httpx.HTTPError:
        logger.exception("Échec de l'envoi vers le connecteur SIEM %s", channel)
        return False

def send_alert_notifications(alert: Alert, threat: Threat | None) -> dict[str, bool]:
    """Diffuse une alerte sur tous les canaux configurés.

    Chaque canal est isolé : une panne Slack ne bloque ni Telegram, ni email,
    ni la création de l'alerte dans la base.
    """

    results: dict[str, bool] = {}
    if settings.webhook_url:
        results["webhook"] = send_alert_webhook(alert, threat)
    if settings.slack_webhook_url:
        results["slack"] = send_slack_notification(alert, threat)
    if settings.telegram_bot_token and settings.telegram_chat_id:
        results["telegram"] = send_telegram_notification(alert, threat)
    if settings.smtp_host and settings.smtp_from and settings.alert_email_to:
        results["email"] = send_email_notification(alert, threat)
    if threat is not None and settings.wazuh_webhook_url:
        auth = f"Bearer {settings.wazuh_token}" if settings.wazuh_token else None
        results["wazuh"] = _send_siem_event(
            channel="Wazuh",
            url=settings.wazuh_webhook_url,
            payload=build_wazuh_event(alert, threat),
            authorization=auth,
        )
    if threat is not None and settings.elastic_siem_url:
        auth = f"ApiKey {settings.elastic_api_key}" if settings.elastic_api_key else None
        results["elastic_siem"] = _send_siem_event(
            channel="Elastic",
            url=settings.elastic_siem_url,
            payload=build_elastic_ecs_event(alert, threat),
            authorization=auth,
        )
    return results
