from types import SimpleNamespace
from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.services.notification_service import send_alert_notifications


def _alert():
    return SimpleNamespace(
        id="alert-1",
        level="critical",
        status="new",
        title="Menace critique",
        message="example.org — score 95/100",
        assigned_to=None,
        created_at=datetime.now(timezone.utc),
    )


def _threat():
    return SimpleNamespace(
        indicator="example.org",
        indicator_type="domain",
        threat_type="phishing",
        risk_score=95,
        risk_level="critical",
        id="threat-1",
        source="otx",
        description="Domaine de phishing",
        first_seen=datetime.now(timezone.utc),
        last_seen=datetime.now(timezone.utc),
    )


def test_multichannel_notifications_are_isolated(monkeypatch):
    calls: list[dict] = []

    def fake_post(url, **kwargs):
        calls.append({"url": url, **kwargs})
        if "slack" in url:
            raise httpx.ConnectError("Slack indisponible")

        class Response:
            def raise_for_status(self):
                return None

        return Response()

    monkeypatch.setattr(settings, "webhook_url", "https://soc.test/events")
    monkeypatch.setattr(settings, "slack_webhook_url", "https://slack.test/hook")
    monkeypatch.setattr(settings, "telegram_bot_token", "bot-secret")
    monkeypatch.setattr(settings, "telegram_chat_id", "123")
    monkeypatch.setattr(httpx, "post", fake_post)

    results = send_alert_notifications(_alert(), _threat())

    assert results == {"webhook": True, "slack": False, "telegram": True}
    assert len(calls) == 3
    telegram_call = next(call for call in calls if "api.telegram.org" in call["url"])
    assert telegram_call["json"]["chat_id"] == "123"
    assert "example.org" in telegram_call["json"]["text"]


def test_email_notification_uses_tls_and_auth(monkeypatch):
    events: list[tuple] = []

    class FakeSmtp:
        def __init__(self, host, port, timeout):
            events.append(("connect", host, port, timeout))

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def starttls(self, context):
            events.append(("starttls",))

        def login(self, username, password):
            events.append(("login", username, password))

        def send_message(self, message):
            events.append(("send", message["To"], message["Subject"]))

    monkeypatch.setattr(settings, "smtp_host", "smtp.test")
    monkeypatch.setattr(settings, "smtp_username", "sentinel")
    monkeypatch.setattr(settings, "smtp_password", "smtp-secret")
    monkeypatch.setattr(settings, "smtp_from", "sentinel@test.local")
    monkeypatch.setattr(settings, "alert_email_to", ["soc@test.local"])
    monkeypatch.setattr("app.services.notification_service.smtplib.SMTP", FakeSmtp)

    results = send_alert_notifications(_alert(), _threat())

    assert results == {"email": True}
    assert ("starttls",) in events
    assert ("login", "sentinel", "smtp-secret") in events
    assert ("send", "soc@test.local", "[Sentinel PME] Alerte CRITICAL") in events


def test_dedicated_siem_connectors_send_vendor_formats(monkeypatch):
    calls: list[dict] = []

    class Response:
        def raise_for_status(self):
            return None

    def fake_post(url, **kwargs):
        calls.append({"url": url, **kwargs})
        return Response()

    monkeypatch.setattr(settings, "wazuh_webhook_url", "https://wazuh.test/events")
    monkeypatch.setattr(settings, "wazuh_token", "wazuh-secret")
    monkeypatch.setattr(settings, "elastic_siem_url", "https://elastic.test/sentinel/_doc")
    monkeypatch.setattr(settings, "elastic_api_key", "elastic-secret")
    monkeypatch.setattr(httpx, "post", fake_post)

    results = send_alert_notifications(_alert(), _threat())

    assert results == {"wazuh": True, "elastic_siem": True}
    wazuh = next(call for call in calls if "wazuh" in call["url"])
    elastic = next(call for call in calls if "elastic" in call["url"])
    assert wazuh["json"]["integration"] == "sentinel-pme"
    assert wazuh["headers"]["Authorization"] == "Bearer wazuh-secret"
    assert elastic["json"]["ecs"]["version"] == "9.3.0"
    assert elastic["headers"]["Authorization"] == "ApiKey elastic-secret"
