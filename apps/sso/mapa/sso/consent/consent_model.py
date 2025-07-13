from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


class Consent(BaseModel):
    """Consent Veri Modeli"""

    id: UUID
    user_id: UUID
    client_id: UUID
    scopes: List[str]
    accepted: bool
    created_at: datetime
    updated_at: Optional[datetime]


class CreateConsent(BaseModel):
    user_id: UUID
    client_id: UUID
    scopes: List[str]
    accepted: bool


class UpdateConsent(BaseModel):
    scopes: List[str]
    accepted: bool
    updated_at: datetime | None = None


class UpdateAllConsent(UpdateConsent):
    pass