from uuid import UUID
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.manage.role_user.role_user_model import CreateRoleUser, UpdateAllRoleUser, UpdateRoleUser, RoleUser
from mapa.manage.role_user.role_user_repository import RoleUserRepository

class RoleUserService(BaseEntityService[RoleUserRepository, RoleUser, CreateRoleUser, UpdateRoleUser, UpdateAllRoleUser]):
    """RoleUser Servisi"""
    
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, RoleUserRepository, RoleUser)

    
    async def get_by_role_user_id(self, role_user_id: UUID, tenant_id: str = None) -> RoleUser:  # type: ignore
        """ID ye göre bilgilerini getirir."""

        return await self.get(role_user_id, tenant_id)