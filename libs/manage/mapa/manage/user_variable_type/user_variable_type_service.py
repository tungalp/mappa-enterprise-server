from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.user_variable_type.user_variable_type_model import CreateUserVariableType, UserVariableType, UpdateAllUserVariableType, UpdateUserVariableType
from mapa.manage.user_variable_type.user_variable_type_repository import UserVariableTypeRepository
from uuid import UUID


class UserVariableTypeService(BaseEntityService[UserVariableTypeRepository, UserVariableType, CreateUserVariableType, UpdateUserVariableType, UpdateAllUserVariableType]):
    """UserVariableTypeService""" 

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, UserVariableTypeRepository, UserVariableType)

    async def get_by_name(self, name: str, tenant_id: str = None) -> UserVariableType:  # type: ignore
        """Client adına uyan kaydı getirir."""

        return await self.find_one(QueryArgs(
            where=[
                Filter(field="name", op=FilterOp.EQUAL, value=name)
            ]
        ), tenant_id)  # type: ignore
    
    async def get_by_user_variable_type_id(self, user_variable_type_id: UUID, tenant_id: str = None) -> UserVariableType:  # type: ignore
        """ID ye göre bilgilerini getirir."""

        return await self.get(user_variable_type_id, tenant_id)