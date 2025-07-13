from typing import List
from uuid import UUID
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.tenant_user.tenant_user_model import CreateTenantUser, TenantUser, UpdateAllTenantUser, UpdateTenantUser
from mapa.manage.tenant_user.tenant_user_repository import TenantUserRepository
from mapa.core.data.base_entity_service import BaseEntityService


class TenantUserService(BaseEntityService[TenantUserRepository, TenantUser, CreateTenantUser, UpdateTenantUser, UpdateAllTenantUser]):
    """Tenant Kullanıcı Servisi"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, TenantUserRepository, TenantUser)

    async def find_by_user_id(self, user_id: UUID) -> List[TenantUser]:
        """Kullanının Tenantlarını getirir."""

        return await self.find(QueryArgs(
            limit=0, offset=0,
            where=[Filter(field="user_id", op=FilterOp.EQUAL, value=user_id)]
        ))
