from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel



class OrganizationRole(BaseModel):
    """OrganizationRole Modeli"""
    id: UUID
    role_id: UUID
    organization_id: UUID 
    role: Any | None = None
    organization: Any | None = None

class CreateOrganizationRole(BaseModel):
    organization_id: UUID
    role_id: UUID 
    
class UpdateOrganizationRole(BaseModel):
    organization_id: UUID
    role_id: UUID 
    
class UpdateAllOrganizationRole(UpdateOrganizationRole):
    pass
