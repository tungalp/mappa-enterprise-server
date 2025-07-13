from typing import Any, List, Optional
from uuid import UUID
import uuid
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.core.data.result import PagingResult
from mapa.manage.client_api.client_api_service import ClientApiService
from mapa.manage.client.client_model import (
    Client,
    ClientInfo,
    CreateClient,
    UpdateAllClient,
    UpdateClient,
)
from mapa.manage.client.client_repository import ClientRepository
from nanoid import generate

from mapa.manage.constants import LevelTypes
from mapa.manage.tenant_client.tenant_client_model import CreateTenantClient
from mapa.manage.tenant_client.tenant_client_service import TenantClientService


class ClientService(
    BaseEntityService[
        ClientRepository, Client, CreateClient, UpdateClient, UpdateAllClient
    ]
):
    """ClientService"""

    def __init__(
        self,
        async_db: AsyncDatabase,
        tenant_client_service: TenantClientService,
        client_api_service: ClientApiService,
    ) -> None:
        self.async_db = async_db
        self.tenant_client_service = tenant_client_service
        self.client_api_service = client_api_service
        super().__init__(async_db, ClientRepository, Client)

    async def create(
        self, client: CreateClient, tenant_id: str | None = None
    ) -> Client:
        """Client oluştururken clientid ve clientsecret atayarak kaydeder."""

        client.client_id = generate(
            alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
            size=32,
        )
        client.client_secret = generate(
            alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
            size=64,
        )
        created_client: Client = await super().create(client)

        created_tenant_client = CreateTenantClient(
            client_id=created_client.id, tenant_id=uuid.UUID(tenant_id)
        )
        await self.tenant_client_service.create(created_tenant_client, tenant_id)

        return created_client

    async def create_all(
        self, clients: List[CreateClient], tenant_id: str | None = None
    ) -> List[Client]:
        """Client oluştururken clientid ve clientsecret atayarak kaydeder."""
        for client in clients:
            client.client_id = generate(
                alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
                size=32,
            )
            client.client_secret = generate(
                alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
                size=64,
            )

        created_clients = await super().create_all(clients)

        create_tenant_clients: List[CreateTenantClient] = []

        for created_client in created_clients:
            create_tenant_clients.append(
                CreateTenantClient(
                    client_id=created_client.id, tenant_id=uuid.UUID(tenant_id)
                )
            )

        await self.tenant_client_service.create_all(create_tenant_clients, tenant_id)

        return created_clients

    async def get(
        self,
        obj_id: Any,
        tenant_id: str | None = None,
        field_list: List[str] | None = None,
    ) -> Client | None:
        """Verilen ID li objeyi istenen alanlarla beraber döndürür."""
        clients = await super().paging(
            QueryArgs(
                where=[
                    Filter(field="id", op=FilterOp.EQUAL, value=obj_id),
                    Filter(
                        field="tenant_client.tenant_id",
                        op=FilterOp.EQUAL,
                        value=tenant_id,
                    ),
                ],
                select=field_list,
            ),
            tenant_id,
        )
        if len(clients.items) == 0:
            return None
        else:
            return clients.items[0]

    # async def find(self, query_args: QueryArgs, tenant_id: str | None = None) -> List[Client]:
    #     """Sorgu parametrelerine uyan kayıtları liste halinde döndürür."""
    #     if query_args.where == None:
    #         query_args.where = []
    #     query_args.where.append(
    #         Filter(field="tenant_client.tenant_id", op=FilterOp.EQUAL, value=tenant_id))
    #     return await super().find(query_args)  # type: ignore

    # async def find_one(self, query_args: QueryArgs, tenant_id: str | None = None) -> Client | None:
    #     """Sorgu parametrelerine uyna kayıtları liste halinde döndürür."""
    #     if query_args.where == None:
    #         query_args.where = []
    #     query_args.where.append(
    #         Filter(field="tenant_client.tenant_id", op=FilterOp.EQUAL, value=tenant_id))
    #     return await super().find_one(query_args)  # type: ignore

    async def paging(
        self, query_args: QueryArgs, tenant_id: str | None = None
    ) -> PagingResult[Client]:
        """Sorgu parametrelerine uyan kayıtları PagingResult sayfa sonuç değeri olarak döndürür."""
        if query_args.where == None:
            query_args.where = []
        query_args.where.append(
            Filter(field="tenant_client.tenant_id", op=FilterOp.EQUAL, value=tenant_id)
        )
        return await super().paging(query_args)  # type: ignore

    async def get_by_name(
        self, name: str, tenant_id: str | None = None
    ) -> Client | None:
        """Client adına uyan kaydı getirir."""

        return await self.find_one(
            QueryArgs(where=[Filter(field="name", op=FilterOp.EQUAL, value=name)]),
            tenant_id,
        )

    async def get_by_client_id(
        self, client_id: str, tenant_id: str | None = None
    ) -> Client | None:
        """Client adına uyan kaydı getirir."""

        return await self.find_one(
            QueryArgs(
                where=[Filter(field="client_id", op=FilterOp.EQUAL, value=client_id)]
            ),
            tenant_id,
        )

    async def get_client_info(
        self, client_id: str, tenant_id: str | None = None
    ) -> ClientInfo | None:
        """Client hakkında genel bilgi verir."""

        client: Client | None = await self.get_by_client_id(client_id, tenant_id)
        if client:
            return ClientInfo(
                client_id=client.client_id,  # type: ignore
                name=client.name,
                description=client.description,
                logo_url=client.logo_url,
                level_type=client.level_type,
            )

    async def delete_all(
        self, query_args: QueryArgs, tenant_id: str | None = None
    ) -> int:
        """Gelen query_args parametresi ile eşleşen kayıtları siler."""
        query_args.offset = 0
        query_args.limit = 0
        if query_args.where == None:
            query_args.where = []
        query_args.where.append(
            Filter(field="tenant_client.tenant_id", op=FilterOp.EQUAL, value=tenant_id)
        )
        return await super().delete_all(query_args, tenant_id)

    async def count(self, query_args: QueryArgs, tenant_id: str | None = None) -> int:
        """Gelen query_args parametresi ile eşleşen kayıtların sayısını döner."""
        if query_args.where == None:
            query_args.where = []
        query_args.where.append(
            Filter(field="tenant_client.tenant_id", op=FilterOp.EQUAL, value=tenant_id)
        )
        return await super().count(query_args, tenant_id)

    async def get_client_scopes(
        self, client_id: str, tenant_id: str | None = None
    ) -> List[str]:
        """Sorgu parametrelerine uyan kayıtların scope listesini List[str] sonuç değeri olarak döndürür."""
        query_args: QueryArgs
        client_scopes: List[str] = []
        try:
            query_args = QueryArgs(
                where=[
                    Filter(
                        field="client_id", op=FilterOp.EQUAL, value=client_id
                    ),
                    Filter(
                        field="tenant_id",
                        op=FilterOp.EQUAL,
                        value=tenant_id,
                    ),
                ],
                select=[
                    "id",
                    "api_id",
                    "client_id",
                    "api_scopes.id",
                    "api_scopes.name",
                    "api_scopes.description",
                    "api_scopes.api_id",
                ],
                limit=0,
                offset=0,
            )
            client_apis = await self.client_api_service.paging(query_args, tenant_id)

            for client_api in client_apis.items:
                    for api_scope in client_api.api_scopes:
                        client_scopes.append(api_scope.name)

            return client_scopes
        except Exception as Ex:
            user_scopes = list(set(client_scopes))
            return user_scopes
