from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class RefreshToken(BaseModel):
    """RefreshToken Modeli"""
    id: UUID
    user_session_id: UUID
    user_id: UUID
    client_id: str
    audience: str
    num_used: int
    is_active: bool
    created_at: datetime
    expired_at: datetime
    last_used_at: datetime | None = None
    nonce: str | None = None


class CreateRefreshToken(BaseModel):
    """Yeni RefreshToken oluşturmak için kullanılan sınıf"""
    user_session_id: UUID
    user_id: UUID
    client_id: str
    audience: str
    created_at: datetime
    expired_at: datetime
    nonce: str | None = None


class UpdateRefreshToken(BaseModel):
    num_used: int | None = None
    last_used_at: datetime | None = None
    is_active: bool | None = None


class UpdateAllRefreshToken(BaseModel):
    ...
