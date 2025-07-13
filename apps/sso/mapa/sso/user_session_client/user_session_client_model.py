from datetime import datetime
from typing import List, Optional
from uuid import UUID  
from pydantic import BaseModel

class UserSessionClient(BaseModel):
    """Kullanıcı Oturum Modeli"""
    
    id: UUID
    user_session_id: UUID
    client_id: UUID
    tenant: UUID
    created_at: datetime


class CreateUserSessionClient(BaseModel):
    user_session_id: UUID
    client_id: UUID
    tenant: UUID
    created_at: datetime
    
    
class UpdateUserSessionClient(BaseModel):
    tenant: UUID
    
class UpdateAllUserSessionClient(UpdateUserSessionClient):
    ...