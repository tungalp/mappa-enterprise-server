from typing import List, Optional
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.client_api_scope.client_api_scope_model import (
    ClientApiScope,
    CreateClientApiScope,
    UpdateAllClientApiScope,
    UpdateClientApiScope,
)
from mapa.manage.client_api_scope.client_api_scope_repository import (
    ClientApiScopeRepository,
)


class ClientApiScopeService(
    BaseEntityService[
        ClientApiScopeRepository,
        ClientApiScope,
        CreateClientApiScope,
        UpdateClientApiScope,
        UpdateAllClientApiScope,
    ]
):
    """ClientApiScope"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, ClientApiScopeRepository, ClientApiScope)

    async def recreate(
        self,
        client_api_scopes: List[CreateClientApiScope],
        tenant_id: str | None = None,
    ) -> List[ClientApiScope]:
        """Mevcut ClientApiScope'ları siler yeniden oluşturur."""
        client_api_scope = client_api_scopes[0] if client_api_scopes else ""
        queryArgs = QueryArgs(
            where=[
                Filter(
                    field="client_api_id",
                    op=FilterOp.EQUAL,
                    value=client_api_scope.client_api_id,
                )  # type: ignore
            ]
        )

        await super().delete_all(queryArgs, tenant_id)
        return await super().create_all(client_api_scopes, tenant_id)
