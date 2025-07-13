from uuid import UUID
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.manage.role_api_scope.role_api_scope_model import CreateRoleApiScope, UpdateAllRoleApiScope, UpdateRoleApiScope, RoleApiScope
from mapa.manage.role_api_scope.role_api_scope_repository import RoleApiScopeRepository

class RoleApiScopeService(BaseEntityService[RoleApiScopeRepository, RoleApiScope, CreateRoleApiScope, UpdateRoleApiScope, UpdateAllRoleApiScope]):
    """RoleApiScope Servisi"""
    
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, RoleApiScopeRepository, RoleApiScope)

    
    async def get_by_role_api_scope_id(self, role_api_scope_id: UUID, tenant_id: str = None) -> RoleApiScope:  # type: ignore
        """ID ye göre bilgilerini getirir."""

        return await self.get(role_api_scope_id, tenant_id)