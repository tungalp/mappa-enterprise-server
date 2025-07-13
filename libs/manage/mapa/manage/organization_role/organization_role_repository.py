from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.manage.organization_role.organization_role_entity import OrganizationRoleEntity


class OrganizationRoleRepository(BaseRepository[OrganizationRoleEntity]):
    """OrganizationRole Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, OrganizationRoleEntity)
