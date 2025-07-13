from uuid import UUID
from pydantic import BaseModel


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
    
class UpdateTenantUser(BaseModel):
    role: str
    
class UpdateAllTenantUser(UpdateTenantUser):
    pass
