from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import bcrypt
import jwt

from app.core.config import settings


def mask_database_url(database_url: str) -> str:
    """Masque les identifiants avant d'écrire une URL de base dans les logs."""

    parsed = urlparse(database_url)
    if not parsed.password:
        return database_url
    return database_url.replace(parsed.password, "***")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(subject: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "role": role, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
