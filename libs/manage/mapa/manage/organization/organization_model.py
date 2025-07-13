from typing import  Dict, Any, Optional,List
from uuid import UUID
from pydantic import BaseModel
from mapa.manage.organization_type.organization_type_model import OrganizationType
from mapa.manage.user.user_model import User


class Organization(BaseModel):
    """Organization Modeli"""
    id: UUID
    name: str
    description:str | None = None
    is_root:bool = False
    parent_id: UUID | None = None
    integration_id:str | None = None
    organization_type_id: UUID
    organization_type: OrganizationType | None = None
    users: List["User"] | None = None
    roles: List[Any] | None = None
    clients: List[Any] | None = None
    is_hierarchical: bool | None = None
    geo: Dict[str, Any] | None = None
    
    client_hierarchical: bool | None = None
    
class CreateOrganization(BaseModel):
    name: str 
    description:str | None = None
    is_root:bool = False
    parent_id: UUID | None = None
    integration_id:str | None = None
    organization_type_id: UUID
    is_hierarchical: bool | None = None
    geo: Dict[str, Any] | None = None

class UpdateOrganization(BaseModel):
    name: str | None = None
    description:str | None = None
    parent_id: UUID | None = None
    integration_id:str | None = None
    organization_type_id: UUID | None = None
    is_hierarchical: bool | None = None
    geo: Dict[str, Any] | None = None

class UpdateAllOrganization(UpdateOrganization):
    pass
    
    
    
class OrganizationEndpoint(BaseModel):
    client_id: str
    tenant_id: str
    info_id: str