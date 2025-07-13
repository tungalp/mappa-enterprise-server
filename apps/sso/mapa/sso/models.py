from datetime import datetime
from typing import  Any, Dict, Optional,List
from uuid import UUID
from pydantic import BaseModel

from mapa.sso.constants import ApplicationTypes, LevelTypes, GrantTypes

class UpdateInvitation(BaseModel):
    used: bool
    organization_id: UUID | None = None
    
    
class CreateOrganization(BaseModel):
    name: str 
    description:str | None = None
    is_root:bool = False
    parent_id: UUID | None = None
    integration_id:str | None = None
    organization_type_id: UUID
    is_hierarchical: bool | None = None
    geo: Dict[str, Any] | None = None
    
class CreateOrganizationType(BaseModel):
    name: str
    description:str | None = None
    is_root:bool = False
    parent_id: UUID | None = None
    
    
class CreateOrganizationUser(BaseModel):
    user_id: UUID
    organization_id: UUID 
    


class CreateTenant(BaseModel):
    name: str
    user_id: UUID
    title: Optional[str]
    session_timeout: int | None = 10800
    
    
    
class TenantUserRole:
    OWNER = "owner"
    MEMBER = "member"

class TenantUser(BaseModel):
    """Tenant Kullanıcı Modeli"""

    id: UUID
    user_id: UUID
    tenant_id: UUID
    role: str

class CreateTenantUser(BaseModel):
    user_id: UUID
    tenant_id: UUID
    role: str
    
    
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
    
    
class Client(BaseModel):
    """Client Modeli"""
    id: UUID
    name: str
    client_id: str | None = None
    client_secret: str | None = None
    redirect_uris: List[str] | None = None
    logout_uris: List[str] | None = None
    client_uri: str | None = None
    description: str | None = None
    application_type: str = ApplicationTypes.WEB
    logo_url: str | None = None
    token_endpoint_auth_method: str | None = None
    web_origins: List[str] | None = None
    cors_origins: List[str] | None = None
    require_consent: bool = True
    is_system: bool = False
    require_pkce: bool = False
    grant_types: List[str]
    level_type: str = LevelTypes.THIRD_PARTY
    id_token_lifetime: int | None = None
    access_token_lifetime: int | None = None
    authorization_code_lifetime: int | None = None
    absolute_refresh_token_lifetime: int | None = None
    sliding_refresh_token_lifetime: int | None = None
    device_code_lifetime: int | None = None
    ciba_lifetime: int | None = None

    refresh_token_rotation: bool | None = None

    jwt_signature_algorithm: str | None = None
    organizations: List[Any]  | None = None

    
class OrganizationType(BaseModel):
    """OrganizationType Modeli"""
    id: UUID
    name: str
    description:str | None = None
    is_root:bool = False
    parent_id: UUID | None = None
    


class Organization(BaseModel):
    """Organization Modeli"""
    id: UUID
    name: str
    description:str | None = None
    is_root:bool = False
    parent_id: UUID | None = None
    integration_id:str | None = None
    organization_type_id: UUID
    organization_type: OrganizationType | None = None
    users: List["User"] | None = None
    roles: List[Any] | None = None
    clients: List[Any] | None = None
    is_hierarchical: bool | None = None
    geo: Dict[str, Any] | None = None
    
    client_hierarchical: bool | None = None
    
class Invitation(BaseModel):
    """Invitation Modeli"""
    id: UUID
    email: str
    user_id: UUID
    expired_at: datetime
    tenant: UUID
    used: bool
    organization_id: UUID
    organization: Organization | None = None
    
    
    

class CreateClient(BaseModel):
    name: str
    client_id: str | None = None
    client_secret: str | None = None
    grant_types: List[str] | None = [GrantTypes.CLIENT_CREDENTIALS,
                                     GrantTypes.AUTHORIZATION_CODE, GrantTypes.REFRESH_TOKEN]
    redirect_uris: List[str] | None = None
    logout_uris: List[str] | None = None
    client_uri: str | None = None
    description: str | None = None
    application_type: str | None = ApplicationTypes.WEB
    logo_url: str | None = None
    token_endpoint_auth_method: str | None = None
    web_origins: List[str] | None = None
    cors_origins: List[str] | None = None
    require_consent: bool | None = True
    require_pkce: bool | None = False
    level_type: str | None = LevelTypes.THIRD_PARTY
    
    
    
class ClientInfo(BaseModel):
    client_id: str
    name: str
    level_type: str
    description: str | None = None
    logo_url: str | None = None
