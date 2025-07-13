from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel



class OrganizationUser(BaseModel):
    """OrganizationUser Modeli"""
    id: UUID
    user_id: UUID
    organization_id: UUID 
    user: Any | None = None
    organization: Any | None = None

class CreateOrganizationUser(BaseModel):
    user_id: UUID
    organization_id: UUID 
    
class UpdateOrganizationUser(BaseModel):
    user_id: UUID
    organization_id: UUID 
    
class UpdateAllOrganizationUser(UpdateOrganizationUser):
    pass
