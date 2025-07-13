from datetime import datetime
from typing import  Optional,List
from uuid import UUID
from pydantic import BaseModel
from mapa.manage.organization.organization_model import Organization

class Invitation(BaseModel):
    """Invitation Modeli"""
    id: UUID
    email: str
    user_id: UUID
    expired_at: datetime
    tenant: UUID
    used: bool
    organization_id: UUID
    organization: Organization | None = None
    
class CreateInvitation(BaseModel):
    email: str
    user_id: UUID
    tenant: UUID
    expired_at: datetime
    organization_id: UUID

class UpdateInvitation(BaseModel):
    used: bool
    organization_id: UUID | None = None

class UpdateAllInvitation(UpdateInvitation):
    pass
    