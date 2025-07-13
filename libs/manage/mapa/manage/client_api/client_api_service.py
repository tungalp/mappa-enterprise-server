from typing import Optional
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.client_api.client_api_model import ClientApi, CreateClientApi, UpdateAllClientApi, UpdateClientApi
from mapa.manage.client_api.client_api_repository import ClientApiRepository 


class ClientApiService(BaseEntityService[ClientApiRepository, ClientApi, CreateClientApi, UpdateClientApi, UpdateAllClientApi]):
    """ClientApi"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, ClientApiRepository, ClientApi)
