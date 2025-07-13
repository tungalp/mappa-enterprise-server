from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.manage.organization_client.organization_client_entity import OrganizationClientEntity


class OrganizationClientRepository(BaseRepository[OrganizationClientEntity]):
    """OrganizationClient Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, OrganizationClientEntity)
