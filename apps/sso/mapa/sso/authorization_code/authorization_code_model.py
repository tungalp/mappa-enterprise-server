from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


class AuthorizationCode(BaseModel):
    """AuthorizationCode Modeli"""
    id: UUID
    code: str
    user_session_id: UUID
    user_id: UUID
    client_id: str
    scopes: List[str]
    redirect_uri: str
    audience: str
    used: bool
    nonce: str
    code_challenge: Optional[str]
    code_challenge_method: Optional[str]
    created_at: datetime
    expired_at: datetime


class CreateAuthorizationCode(BaseModel):
    """Yeni AuthorizationCode oluşturmak için kullanılan sınıf"""
    user_session_id: UUID
    user_id: UUID
    client_id: str
    code :str    
    scopes: List[str]
    redirect_uri: str
    audience: str
    nonce: str
    code_challenge: str | None = None
    code_challenge_method: str | None = None
    created_at: datetime
    expired_at: datetime    


class UpdateAuthorizationCode(BaseModel):
    used: bool
    
class UpdateAllAuthorizationCode(BaseModel):
    ...