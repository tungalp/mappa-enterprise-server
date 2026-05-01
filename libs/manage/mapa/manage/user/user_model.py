from datetime import datetime
from typing import Optional, Dict, List, Any
from uuid import UUID
from pydantic import BaseModel


class User(BaseModel):
    """User Modeli"""

    id: UUID
    subject_id: str
    source: str = "local"
    name: str
    surname: str
    email: str
    email_verified: bool | None = None
    phone: str | None = None
    created_at: datetime
    last_tenant_id: UUID | None = None
    provider: str | None = None
    provider_user_id: UUID | None = None
    profile_adaptor_id: UUID | None = None
    roles: List[Any] | None = None
    organizations: List[Any] | None = None
    tenant: str | None = None
    blocked: bool = False
    picture: str | None = None
    openid: str | None = None
    address: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    nickname: str | None = None
    offline_access: bool | None = None
    tenant_users: List[Any] | None = None
    context: Dict[str, Any] | None = None
    is_ldap_user: bool | None = None
    ldap_server_id: UUID | None = None


class UserMinimal(BaseModel):
    """Kısıtlı User Modeli (Arama sonuçları için)"""

    id: UUID
    subject_id: str
    name: str
    surname: str
    email: str
    picture: str | None = None


class CreateUser(BaseModel):
    subject_id: str | None = None
    name: str
    surname: str
    email: str
    password: str
    phone: str | None = None
    blocked: bool = False
    email_verified: bool | None = None
    context: Dict[str, Any] | None = None
    is_ldap_user: bool | None = None
    ldap_server_id: UUID | None = None


class UpdateUser(BaseModel):
    email_verified: bool | None = None
    blocked: bool = False
    password: str | None = None
    name: str | None = None
    surname: str | None = None
    email: str | None = None
    phone: str | None = None
    provider: str | None = None
    provider_user_id: UUID | None = None
    profile_adaptor_id: UUID | None = None
    picture: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    nickname: str | None = None
    address: str | None = None
    context: Dict[str, Any] | None = None


class UpdateAllUser(UpdateUser):
    pass
