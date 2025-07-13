from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel



class OrganizationClient(BaseModel):
    """OrganizationClient Modeli"""
    id: UUID
    client_id: str
    organization_id: UUID 
    client: Any | None = None
    organization: Any | None = None
    is_hierarchical: bool = False

class CreateOrganizationClient(BaseModel):
    organization_id: UUID
    client_id: str
    is_hierarchical: bool = False
    
class UpdateOrganizationClient(BaseModel):
    organization_id: UUID
    client_id: str
    is_hierarchical: bool
    
class UpdateAllOrganizationClient(UpdateOrganizationClient):
    is_hierarchical: bool
