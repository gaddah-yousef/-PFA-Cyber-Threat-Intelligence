from datetime import datetime
from enum import Enum

import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, TypeAdapter, field_validator


class UserRole(str, Enum):
    admin = "admin"
    analyst = "analyst"
    viewer = "viewer"


class UserCreate(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.viewer

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        if re.fullmatch(r"[^@\s]+@(?:[a-z0-9-]+\.)*local", value):
            return value
        return str(TypeAdapter(EmailStr).validate_python(value))


class UserRead(BaseModel):
    id: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    role: UserRole | None = None
    is_active: bool | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    email: str


class TokenPayload(BaseModel):
    sub: str
    role: UserRole
    exp: int
