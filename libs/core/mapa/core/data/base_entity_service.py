from typing import Any, Dict, Generic, List, Type, TypeVar

from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_repository import BaseRepository
from mapa.core.data.base_service import BaseService
from mapa.core.data.query_args import QueryArgs
from pydantic import BaseModel

from mapa.core.data.result import PagingResult

RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)
ModelType = TypeVar("ModelType", bound=BaseModel)
CreateType = TypeVar("CreateType", bound=BaseModel)
UpdateType = TypeVar("UpdateType", bound=BaseModel)
UpdateAllType = TypeVar("UpdateAllType", bound=BaseModel)


class BaseEntityService(BaseService, Generic[RepositoryType, ModelType, CreateType, UpdateType, UpdateAllType]):
    """Belli bir entity sınıfına bağlı olan repository sınıfını direk olarak kullanan servisler
    bu sınıftan türetilir.
    """

    repo: RepositoryType
    model_type: ModelType

    def __init__(
        self,
        async_db: AsyncDatabase,
        repo_type: Type[RepositoryType],
        model_type: Type[ModelType]
    ) -> None:
        self.repo = repo_type(async_db)
        self.model_type = model_type
        super().__init__()

    async def get(self, obj_id: Any, tenant_id: str | None = None, field_list: List[str | Dict[str, Any]] | None = None) -> ModelType:
        """Verilen ID li objeyi istenen alanlarla beraber döndürür.
        """
        fields = field_list
        if field_list and len(field_list) > 0:
            if any(isinstance(field, dict) for field in field_list):
                fields = []
                self.repo.extract_fields_from_model(fields, field_list, None)
            
        db_obj = await self.repo.get(obj_id, tenant_id, fields)
        ret_val: ModelType = None
        if db_obj:
            ret_val = self.model_type.model_validate(
                self.repo.dict(db_obj, fields))
        return ret_val

    async def find(self, query_args: QueryArgs, tenant_id: str | None = None) -> List[ModelType]:
        """Sorgu parametrelerine uyan kayıtları liste halinde döndürür."""

        db_obj_list = await self.repo.find(query_args, tenant_id)

        ret_val: List[ModelType] = [
            self.model_type.model_validate(
                self.repo.dict(db_obj, query_args.select)
            ) for db_obj in db_obj_list
        ]
        return ret_val

    async def find_one(self, query_args: QueryArgs, tenant_id: str | None = None) -> ModelType | None:
        """Sorgu parametrelerine uyna kayıtları liste halinde döndürür."""

        db_obj = await self.repo.find_one(query_args, tenant_id)
        ret_val: ModelType | None = None
        if db_obj:
            ret_val = self.model_type.model_validate(
                self.repo.dict(db_obj, query_args.select))
        return ret_val

    async def paging(self, query_args: QueryArgs, tenant_id: str | None = None) -> PagingResult[ModelType]:
        """Sorgu parametrelerine uyan kayıtları PagingResult sayfa sonuç değeri olarak döndürür."""

        total = await self.repo.count(query_args, tenant_id)
        items = await self.find(query_args, tenant_id)
        return PagingResult[ModelType](
            total=total,
            items=items,
            limit=query_args.limit,
            offset=query_args.offset
        )

    async def create(self, input_obj: CreateType, tenant_id: str | None = None, user_id: str | None = None ) -> ModelType:
        """Yeni bir model oluşturur"""

        db_obj = await self.repo.create(input_obj.model_dump(exclude_unset=True), tenant_id, user_id)
        ret_val = self.model_type.model_validate(self.repo.dict(db_obj))
        return ret_val

    async def create_all(self, input_objs: List[CreateType], tenant_id: str | None = None, user_id: str | None = None ) -> List[ModelType]:
        """Yeni bir model oluşturur"""

        dict_objs = [input_obj.model_dump(exclude_unset=True) for input_obj in input_objs]
        db_objs = await self.repo.create_all(dict_objs, tenant_id, user_id)
        ret_val: List[ModelType] = [
            self.model_type.model_validate(
                self.repo.dict(db_obj)
            ) for db_obj in db_objs
        ]
        return ret_val


    async def update(self, obj_id: Any, input_obj: UpdateType, tenant_id: str | None = None, user_id: str | None = None ) -> ModelType | None:
        """Verilen modeli günceller"""

        db_obj = await self.repo.update(obj_id, input_obj.model_dump(exclude_unset=True), tenant_id, user_id)
        ret_val: ModelType | None = None
        if db_obj:
            ret_val = self.model_type.model_validate(self.repo.dict(db_obj))
        return ret_val

    async def update_by_ids(self, obj_ids: List[Any], input_obj: UpdateType, tenant_id: str | None = None, user_id: str | None = None ) -> bool:
        """Verilen modeli günceller"""

        ret_val = await self.repo.update_by_ids(obj_ids, input_obj.model_dump(exclude_unset=True), tenant_id, user_id)
        return ret_val

    async def update_all(self, query_args: QueryArgs, input_obj: UpdateAllType, tenant_id: str | None = None, user_id: str | None = None ) -> int:
        """Sorgu sonucunda gelen kayıtları verilen modeldeki değerlerle günceller"""

        ret_val = await self.repo.update_all(query_args, input_obj.model_dump(exclude_unset=True), tenant_id, user_id)
        return ret_val

    async def delete(self, obj_id: Any, tenant_id: str | None = None) -> bool:
        """obj_id değerindeki kaydı siler"""

        ret_val = await self.repo.delete(obj_id, tenant_id)
        return ret_val

    async def delete_by_ids(self, obj_ids: List[Any], tenant_id: str | None = None) -> int:
        """obj_ids listesindeki kayıtları siler"""

        ret_val = await self.repo.delete_by_ids(obj_ids, tenant_id)
        return ret_val

    async def delete_all(self, query_args: QueryArgs, tenant_id: str | None = None) -> int:
        """Yeni bir model oluşturur"""

        ret_val = await self.repo.delete_all(query_args, tenant_id)
        return ret_val

    async def count(self, query_args: QueryArgs, tenant_id: str | None = None) -> int:
        """Sorgu parametrelerine uyan kayıtları PagingResult sayfa sonuç değeri olarak döndürür."""
        return await self.repo.count(query_args, tenant_id)
