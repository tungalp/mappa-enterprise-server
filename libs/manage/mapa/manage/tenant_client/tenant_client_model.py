from uuid import UUID
from pydantic import BaseModel
from mapa.manage.client.client_model import Client


class TenantClient(BaseModel):
    """Tenant Kullanıcı Modeli"""

    id: UUID
    client_id: UUID
    client: Client | None = None
    tenant_id: UUID


class CreateTenantClient(BaseModel):
    client_id: UUID
    tenant_id: UUID


class UpdateTenantClient(BaseModel):
    pass


class UpdateAllTenantClient(UpdateTenantClient):
    pass
