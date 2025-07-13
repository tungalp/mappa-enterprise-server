from typing import Optional
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.api_scope.api_scope_model import ApiScope, CreateApiScope, UpdateAllApiScope, UpdateApiScope
from mapa.manage.api_scope.api_scope_repository import ApiScopeRepository 


class ApiScopeService(BaseEntityService[ApiScopeRepository, ApiScope, CreateApiScope, UpdateApiScope, UpdateAllApiScope]):
    """ApiScope"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, ApiScopeRepository, ApiScope)
