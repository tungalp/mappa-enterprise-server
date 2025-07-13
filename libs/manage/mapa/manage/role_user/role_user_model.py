from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel



class RoleUser(BaseModel):
    """RoleUser Modeli"""
    id: UUID
    expired_at: datetime
    user_id: UUID
    role_id: UUID 
    user: Any | None = None
    role: Any | None = None

class CreateRoleUser(BaseModel):
    expired_at: datetime
    user_id: UUID
    role_id: UUID 
    
class UpdateRoleUser(BaseModel):
    expired_at: datetime
    user_id: UUID
    role_id: UUID 
    
class UpdateAllRoleUser(UpdateRoleUser):
    pass
