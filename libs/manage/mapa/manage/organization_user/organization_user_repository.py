from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.manage.organization_user.organization_user_entity import OrganizationUserEntity


class OrganizationUserRepository(BaseRepository[OrganizationUserEntity]):
    """OrganizationUser Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, OrganizationUserEntity)
