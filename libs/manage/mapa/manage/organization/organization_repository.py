from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.manage.organization.organization_entity import OrganizationEntity


class OrganizationRepository(BaseRepository[OrganizationEntity]):
    """Organization Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, OrganizationEntity)
