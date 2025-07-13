from typing import  Any, Optional,List
from uuid import UUID
from pydantic import BaseModel
from mapa.manage.user.user_model import User
from mapa.manage.api_scope.api_scope_model import ApiScope


class Role(BaseModel):
    """Role Modeli"""
    id: UUID
    name: str
    description:str
    users: List["User"] | None = None
    api_scopes: List[ApiScope] | None = None
    organizations: List[Any] | None = None

class CreateRole(BaseModel):
    name: str
    description:str

class UpdateRole(BaseModel):
    name: str | None = None
    description: str | None = None

class UpdateAllRole(UpdateRole):
    pass
    