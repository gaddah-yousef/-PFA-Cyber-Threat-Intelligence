import os
from collections.abc import Generator
from unittest.mock import patch

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_pme_threats.db")
os.environ.setdefault("ENVIRONMENT", "test")

# Les tests ne doivent jamais reprendre les destinations ou secrets locaux du
# fichier .env : une alerte de test ne doit produire aucun effet externe.
for external_setting in (
    "NVD_API_KEY",
    "OTX_API_KEY",
    "ABUSEIPDB_API_KEY",
    "URLHAUS_AUTH_KEY",
    "WEBHOOK_URL",
    "WEBHOOK_SECRET",
    "SLACK_WEBHOOK_URL",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "WAZUH_WEBHOOK_URL",
    "WAZUH_TOKEN",
    "ELASTIC_SIEM_URL",
    "ELASTIC_API_KEY",
    "SMTP_HOST",
    "SMTP_USERNAME",
    "SMTP_PASSWORD",
    "SMTP_FROM",
    "ALERT_EMAIL_TO",
    "REDIS_URL",
):
    os.environ[external_setting] = ""

from fastapi.testclient import TestClient  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

for optional_setting in (
    "nvd_api_key",
    "otx_api_key",
    "abuseipdb_api_key",
    "urlhaus_auth_key",
    "webhook_url",
    "webhook_secret",
    "slack_webhook_url",
    "telegram_bot_token",
    "telegram_chat_id",
    "wazuh_webhook_url",
    "wazuh_token",
    "elastic_siem_url",
    "elastic_api_key",
    "smtp_host",
    "smtp_username",
    "smtp_password",
    "smtp_from",
    "redis_url",
):
    setattr(settings, optional_setting, None)
settings.alert_email_to = []


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    Base.metadata.drop_all(bind=engine)
    with (
        patch("app.main.start_scheduler"),
        patch("app.main.stop_scheduler"),
        TestClient(app) as test_client,
    ):
        yield test_client
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/auth/login",
        data={"username": settings.admin_email, "password": settings.admin_password},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
