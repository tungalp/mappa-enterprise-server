from mapa.core.rabbitmq.base_connection import RabbitConnection
from mapa.core.rabbitmq.base_consumer import BaseConsumer
from mapa.manage.client.client_model import CreateClient, UpdateClient
from mapa.manage.client.client_service import ClientService
from mapa.core.data.query_args import QueryArgs
from redis.asyncio import Redis


class ClientCreateConsumer(BaseConsumer):
    def __init__(
        self,
        client_service: ClientService,
        connection: RabbitConnection,
        rredis: Redis,
        wredis: Redis,
    ):
        super().__init__(
            "client.create", "client.create", "mapa-exchange", connection, rredis, wredis
        )
        self.client_service = client_service

    async def process_message(self, payload: dict) -> dict:
        data = payload["data"]
        client = CreateClient(**data)
        tenant_id = payload.get("tenant_id")
        created = await self.client_service.create(client, tenant_id)
        return {
            "id": created.id,
            "client_id": created.client_id,
            "client_secret": created.client_secret,
        }


class ClientUpdateConsumer(BaseConsumer):
    def __init__(
        self,
        client_service: ClientService,
        connection: RabbitConnection,
        rredis: Redis,
        wredis: Redis,
    ):
        super().__init__(
            "client.update", "client.update", "mapa-exchange", connection, rredis, wredis
        )
        self.client_service = client_service

    async def process_message(self, payload: dict) -> dict:
        data = payload["data"]
        id = payload["id"]
        client = UpdateClient(**data)
        tenant_id = payload.get("tenant_id")
        updated = await self.client_service.update(id, client, tenant_id)
        return {"id": id}


class ClientDeleteConsumer(BaseConsumer):
    def __init__(
        self,
        client_service: ClientService,
        connection: RabbitConnection,
        rredis: Redis,
        wredis: Redis,
    ):
        super().__init__(
            "client.delete", "client.delete", "mapa-exchange", connection, rredis, wredis
        )
        self.client_service = client_service

    async def process_message(self, payload: dict) -> bool:
        client_id = payload["id"]
        tenant_id = payload.get("tenant_id")
        result = await self.client_service.delete(client_id, tenant_id)
        return result


class ClientGetByClientIdConsumer(BaseConsumer):
    def __init__(
        self,
        client_service: ClientService,
        connection: RabbitConnection,
        rredis: Redis,
        wredis: Redis,
    ):
        super().__init__(
            "client.get_client_by_client_id",
            "client.get_client_by_client_id",
            "mapa-exchange",
            connection,
            rredis,
            wredis,
        )
        self.client_service = client_service

    async def process_message(self, payload: dict) -> dict:
        client_id = payload["client_id"]
        tenant_id = payload.get("tenant_id")
        client = await self.client_service.get_by_client_id(client_id, tenant_id)
        if client is None:
            return {}
        return client.model_dump()  # type: ignore


class ClientGetConsumer(BaseConsumer):
    def __init__(
        self,
        client_service: ClientService,
        connection: RabbitConnection,
        rredis: Redis,
        wredis: Redis,
    ):
        super().__init__(
            "client.get", "client.get", "mapa-exchange", connection, rredis, wredis
        )
        self.client_service = client_service

    async def process_message(self, payload: dict) -> dict:
        api_id = payload["id"]
        tenant_id = payload.get("tenant_id")
        fields = payload.get("fields", [])
        result = await self.client_service.get(api_id, tenant_id, fields)
        if result is None:
            return {}
        return result.model_dump()  # type: ignore


class ClientDeleteAllConsumer(BaseConsumer):
    def __init__(
        self,
        client_service: ClientService,
        connection: RabbitConnection,
        rredis: Redis,
        wredis: Redis,
    ):
        super().__init__(
            "client.delete_all",
            "client.delete_all",
            "mapa-exchange",
            connection,
            rredis,
            wredis,
        )
        self.client_service = client_service

    async def process_message(self, payload: dict) -> int:
        query_args = payload["query_args"]
        tenant_id = payload.get("tenant_id")
        result = await self.client_service.delete_all(
            QueryArgs(**query_args), tenant_id
        )
        return result


class ClientPagingConsumer(BaseConsumer):
    def __init__(
        self,
        client_service: ClientService,
        connection: RabbitConnection,
        rredis: Redis,
        wredis: Redis,
    ):
        super().__init__(
            "client.paging", "client.paging", "mapa-exchange", connection, rredis, wredis
        )
        self.client_service = client_service

    async def process_message(self, payload: dict) -> dict:
        query_args = payload["query_args"]
        tenant_id = payload.get("tenant_id")
        clients = await self.client_service.paging(QueryArgs(**query_args), tenant_id)
        return clients.model_dump()  # type: ignore


class ClientFindConsumer(BaseConsumer):
    def __init__(
        self,
        client_service: ClientService,
        connection: RabbitConnection,
        rredis: Redis,
        wredis: Redis,
    ):
        super().__init__(
            "client.find", "client.find", "mapa-exchange", connection, rredis, wredis
        )
        self.client_service = client_service

    async def process_message(self, payload: dict) -> dict:
        query_args = payload["query_args"]
        tenant_id = payload.get("tenant_id")
        clients = await self.client_service.find(QueryArgs(**query_args), tenant_id)
        serialized_clients = [
            client.model_dump() if hasattr(client, "model_dump") else client
            for client in clients
        ]
        return {"clients": serialized_clients}


class ClientGetInfoConsumer(BaseConsumer):
    def __init__(
        self,
        client_service: ClientService,
        connection: RabbitConnection,
        rredis: Redis,
        wredis: Redis,
    ):
        super().__init__(
            "client.get_client_info",
            "client.get_client_info",
            "mapa-exchange",
            connection,
            rredis,
            wredis,
        )
        self.client_service = client_service

    async def process_message(self, payload: dict) -> dict:
        client_id = payload["client_id"]
        tenant_id = payload.get("tenant_id")
        client_info = await self.client_service.get_client_info(client_id, tenant_id)
        if client_info is None:
            return {}
        return client_info.model_dump()  # type: ignore


class ClientGetScopesConsumer(BaseConsumer):
    def __init__(
        self,
        client_service: ClientService,
        connection: RabbitConnection,
        rredis: Redis,
        wredis: Redis,
    ):
        super().__init__(
            "client.get_client_scopes",
            "client.get_client_scopes",
            "mapa-exchange",
            connection,
            rredis,
            wredis,
        )
        self.service = client_service

    async def process_message(self, payload: dict) -> list[str]:
        client_id = payload["client_id"]
        tenant_id = payload.get("tenant_id")
        result = await self.service.get_client_scopes(client_id, tenant_id)
        if result is None:
            return []
        return result
