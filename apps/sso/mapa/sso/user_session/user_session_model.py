from datetime import datetime
from typing import List, Optional
from uuid import UUID  
from pydantic import BaseModel

class UserSession(BaseModel):
    """Kullanıcı Oturum Modeli"""
    
    id: UUID
    user_id: UUID
    authenticated_at: datetime
    expired_at: datetime
    authenticated: bool

class CreateUserSession(BaseModel):
    id: UUID
    user_id: UUID
    authenticated_at: datetime
    expired_at: datetime
    authenticated: bool
    
    
class UpdateUserSession(BaseModel):
    expired_at: datetime | None = None
    authenticated: bool | None = None
    authenticated_at: datetime | None = None
    
class UpdateAllUserSession(UpdateUserSession):
    pass