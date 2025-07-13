from uuid import UUID
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.manage.organization_role.organization_role_model import CreateOrganizationRole, UpdateAllOrganizationRole, UpdateOrganizationRole, OrganizationRole
from mapa.manage.organization_role.organization_role_repository import OrganizationRoleRepository

class OrganizationRoleService(BaseEntityService[OrganizationRoleRepository, OrganizationRole, CreateOrganizationRole, UpdateOrganizationRole, UpdateAllOrganizationRole]):
    """OrganizationRole Servisi"""
    
    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, OrganizationRoleRepository, OrganizationRole)

    
    async def get_by_organization_role_id(self, organization_role_id: UUID, tenant_id: str = None) -> OrganizationRole:  # type: ignore
        """ID ye göre bilgilerini getirir."""

        return await self.get(organization_role_id, tenant_id)