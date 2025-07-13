from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.role.role_model import CreateRole, Role, UpdateAllRole, UpdateRole
from mapa.manage.role.role_repository import RoleRepository
from uuid import UUID


class RoleService(BaseEntityService[RoleRepository, Role, CreateRole, UpdateRole, UpdateAllRole]):
    """RoleService""" 

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, RoleRepository, Role)

    async def get_by_name(self, name: str, tenant_id: str = None) -> Role:  # type: ignore
        """Client adına uyan kaydı getirir."""

        return await self.find_one(QueryArgs(
            where=[
                Filter(field="name", op=FilterOp.EQUAL, value=name)
            ]
        ), tenant_id)  # type: ignore
    
    async def get_by_role_id(self, role_id: UUID, tenant_id: str = None) -> Role:  # type: ignore
        """ID ye göre bilgilerini getirir."""

        return await self.get(role_id, tenant_id)