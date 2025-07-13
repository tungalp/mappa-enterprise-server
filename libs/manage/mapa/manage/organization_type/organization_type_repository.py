from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.manage.organization_type.organization_type_entity import OrganizationTypeEntity


class OrganizationTypeRepository(BaseRepository[OrganizationTypeEntity]):
    """OrganizationType Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, OrganizationTypeEntity)
