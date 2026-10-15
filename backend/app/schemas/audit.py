from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    id: str
    actor_email: str
    actor_role: str
    action: str
    target_type: str | None
    target_id: str | None
    details: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
