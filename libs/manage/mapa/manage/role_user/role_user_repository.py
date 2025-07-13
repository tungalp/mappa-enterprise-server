from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.manage.role_user.role_user_entity import RoleUserEntity


class RoleUserRepository(BaseRepository[RoleUserEntity]):
    """RoleUser Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, RoleUserEntity)
