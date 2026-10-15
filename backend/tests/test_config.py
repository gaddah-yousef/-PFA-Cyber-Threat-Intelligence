import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_rejects_default_admin_password():
    with pytest.raises(ValidationError, match="ADMIN_PASSWORD"):
        Settings(
            environment="production",
            jwt_secret_key="a-production-secret-that-is-long-and-random",
            admin_password="ChangeMe123!",
            _env_file=None,
        )


def test_production_accepts_explicit_admin_password():
    settings = Settings(
        environment="production",
        jwt_secret_key="a-production-secret-that-is-long-and-random",
        admin_password="A-different-production-password-2026!",
        _env_file=None,
    )

    assert settings.environment == "production"
