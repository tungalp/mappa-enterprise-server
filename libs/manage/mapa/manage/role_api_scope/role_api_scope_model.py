
from typing import Any
from uuid import UUID
from pydantic import BaseModel


class RoleApiScope(BaseModel):
    """RoleApiScope Modeli"""
    id: UUID
    role_id: UUID
    api_scope_id: UUID
    role: Any | None = None
    api_scope: Any | None = None
  

class CreateRoleApiScope(BaseModel):
    role_id: UUID
    api_scope_id: UUID
    
class UpdateRoleApiScope(BaseModel):
    role_id: UUID
    api_scope_id: UUID
    
class UpdateAllRoleApiScope(UpdateRoleApiScope):
    pass
