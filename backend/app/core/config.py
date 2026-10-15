from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration chargée depuis l'environnement ou un fichier .env."""

    app_name: str = "PME Cyber Threat Early Warning System"
    app_version: str = "1.0.0"
    environment: str = "development"
    database_url: str = "sqlite:///./pme_threats.db"
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )
    nvd_api_key: str | None = None
    otx_api_key: str | None = None
    abuseipdb_api_key: str | None = None
    urlhaus_auth_key: str | None = None

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8

    admin_email: str = "admin@pme-cyber.local"
    admin_password: str = "ChangeMe123!"

    collector_interval_minutes: int = 60
    abuseipdb_interval_minutes: int = 360

    # Notification SOC optionnelle : si définie, chaque nouvelle alerte est
    # poussée vers ce webhook (SOAR, Slack via un relais, n8n, etc.).
    webhook_url: str | None = None
    webhook_secret: str | None = None
    webhook_timeout_seconds: float = 5.0

    # Canaux directs optionnels. Aucun secret n'est requis si le canal reste
    # désactivé ; une configuration incomplète est simplement ignorée.
    slack_webhook_url: str | None = None
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    wazuh_webhook_url: str | None = None
    wazuh_token: str | None = None
    elastic_siem_url: str | None = None
    elastic_api_key: str | None = None
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None
    smtp_starttls: bool = True
    alert_email_to: Annotated[list[str], NoDecode] = Field(default_factory=list)

    # File de tâches optionnelle pour déplacer les collectes longues hors du
    # processus web. Activée dans le déploiement production avec Redis/RQ.
    redis_url: str | None = None
    task_queue_name: str = "sentinel-collectors"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("alert_email_to", mode="before")
    @classmethod
    def parse_alert_recipients(cls, value: object) -> object:
        if isinstance(value, str):
            return [recipient.strip() for recipient in value.split(",") if recipient.strip()]
        return value

    @field_validator("jwt_secret_key")
    @classmethod
    def forbid_default_secret_in_production(cls, value: str, info) -> str:
        environment = info.data.get("environment", "development")
        if environment == "production" and value == "change-me-in-production":
            raise ValueError("JWT_SECRET_KEY doit être défini explicitement en production")
        return value

    @field_validator("admin_password")
    @classmethod
    def forbid_default_admin_password_in_production(cls, value: str, info) -> str:
        environment = info.data.get("environment", "development")
        if environment == "production" and value == "ChangeMe123!":
            raise ValueError("ADMIN_PASSWORD doit être défini explicitement en production")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
