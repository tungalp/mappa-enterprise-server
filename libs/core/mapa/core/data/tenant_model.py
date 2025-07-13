from uuid import UUID
from pydantic import BaseModel


class TenantModel(BaseModel):
    """Tenant bazlı veri modelleri için kullanılan ortak model"""    

    tenant_id: UUID