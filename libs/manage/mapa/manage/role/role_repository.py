from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.manage.role.role_entity import RoleEntity


class RoleRepository(BaseRepository[RoleEntity]):
    """Role Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, RoleEntity)
