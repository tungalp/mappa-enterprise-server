from typing import Optional
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.api.api_model import Api, CreateApi, UpdateAllApi, UpdateApi
from mapa.manage.api.api_repository import ApiRepository 


class ApiService(BaseEntityService[ApiRepository, Api, CreateApi, UpdateApi, UpdateAllApi]):
    """Api"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, ApiRepository, Api)
