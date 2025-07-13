from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.manage.user_variable_type.user_variable_type_entity import UserVariableTypeEntity


class UserVariableTypeRepository(BaseRepository[UserVariableTypeEntity]):
    """Role Repo"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, UserVariableTypeEntity)
