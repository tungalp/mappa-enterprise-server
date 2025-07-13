from typing import  Optional,List
from uuid import UUID
from pydantic import BaseModel

class OrganizationType(BaseModel):
    """OrganizationType Modeli"""
    id: UUID
    name: str
    description:str | None = None
    is_root:bool = False
    parent_id: UUID | None = None
    

class CreateOrganizationType(BaseModel):
    name: str
    description:str | None = None
    is_root:bool = False
    parent_id: UUID | None = None
    
class UpdateOrganizationType(BaseModel):
    name: str | None = None
    description:str | None = None
    parent_id: UUID | None = None

class UpdateAllOrganizationType(UpdateOrganizationType):
    pass
    