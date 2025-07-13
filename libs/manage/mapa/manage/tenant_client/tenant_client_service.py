from uuid import UUID
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.tenant_client.tenant_client_model import CreateTenantClient, TenantClient, UpdateAllTenantClient, UpdateTenantClient
from mapa.manage.tenant_client.tenant_client_repository import TenantClientRepository
from mapa.core.data.base_entity_service import BaseEntityService


class TenantClientService(BaseEntityService[TenantClientRepository, TenantClient, CreateTenantClient, UpdateTenantClient, UpdateAllTenantClient]):
    """Tenant Kullanıcı Servisi"""
    
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, TenantClientRepository, TenantClient)

    async def find_by_client_id(self, client_id: str) -> TenantClient | None:
        return await self.find_one(QueryArgs(where=[
            Filter(field="client_id", op=FilterOp.EQUAL, value=client_id)
        ]))