from typing import List
from uuid import UUID
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.tenant.tenant_model import CreateTenant, Tenant, UpdateAllTenant, UpdateTenant
from mapa.manage.tenant.tenant_repository import TenantRepository


class TenantService(BaseEntityService[TenantRepository, Tenant, CreateTenant, UpdateTenant, UpdateAllTenant]):
    """Tenant Service"""
    
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, TenantRepository, Tenant)

    async def get_by_user_id(self, user_id: UUID) -> Tenant | None:
        return await self.find_one(QueryArgs(where=[
            Filter(field="user_id", op=FilterOp.EQUAL, value=user_id)
        ]))