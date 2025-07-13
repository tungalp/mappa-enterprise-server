from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.manage.role_api_scope.role_api_scope_entity import RoleApiScopeEntity


class RoleApiScopeRepository(BaseRepository[RoleApiScopeEntity]):
    """RoleApiScope Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, RoleApiScopeEntity)
