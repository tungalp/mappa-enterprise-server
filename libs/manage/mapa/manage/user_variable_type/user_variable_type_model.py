from typing import  Any, Optional,List
from uuid import UUID
from pydantic import BaseModel
from mapa.manage.user.user_model import User
from mapa.manage.api_scope.api_scope_model import ApiScope


class UserVariableType(BaseModel):
    """UserVariableType Modeli"""
    id: UUID
    name: str
    description:str
    
class CreateUserVariableType(BaseModel):
    name: str
    description:str | None = None

class UpdateUserVariableType(BaseModel):
    name: str
    description: str | None = None

class UpdateAllUserVariableType(BaseModel):
    description: str | None = None
    