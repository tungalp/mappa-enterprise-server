from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class Tenant(BaseModel):
    """Tenant"""

    id: UUID
    name: str
    user_id: UUID
    title: Optional[str]
    session_timeout: int


class CreateTenant(BaseModel):
    name: str
    user_id: UUID
    title: Optional[str]
    session_timeout: int | None = 10800

class UpdateTenant(BaseModel):
    name: Optional[str]
    user_id: Optional[UUID]
    title: Optional[str]
    session_timeout: Optional[int]


class UpdateAllTenant(UpdateTenant):
    pass
