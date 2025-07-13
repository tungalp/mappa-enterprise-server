from mapa.core.data.query_args import QueryArgs
from mapa.core.rabbitmq.base_connection import RabbitConnection
from mapa.core.rabbitmq.base_consumer import BaseConsumer
from mapa.manage.ldap_server.ldap_server_service import LdapServerService
from mapa.manage.user.user_model import CreateUser
from mapa.manage.user.user_service import UserService
from redis.asyncio import Redis


class UserCreateConsumer(BaseConsumer):
    def __init__(
        self,
        user_service: UserService,
        connection: RabbitConnection,
        rredis: Redis,
        wredis: Redis,
    ):
        super().__init__(
            "user.create", "user.create", "mapa-exchange", connection, rredis, wredis
        )
        self.user_service = user_service

    async def process_message(self, payload: dict) -> dict:
        data = payload["data"]
        user = CreateUser(**data)
        tenant_id = payload.get("tenant_id")
        created = await self.user_service.create(user, tenant_id)
        return {
            "id": created.id,
            "name": created.name,
            "surname": created.surname,
            "email": created.email,
        }


class UserLdapCheckConnectionConsumer(BaseConsumer):
    def __init__(
        self,
        service: LdapServerService,
        connection: RabbitConnection,
        rredis: Redis,
        wredis: Redis,
    ):
        super().__init__(
            "user.ldap.check_connection",
            "user.ldap.check_connection",
            "mapa-exchange",
            connection,
            rredis,
            wredis,
        )
        self.service = service

    async def process_message(self, payload: dict) -> dict:
        ldap_server_id = payload["ldap_server_id"]
        email = payload["email"]
        password = payload["password"]
        bool = await self.service.check_ldap_connection_with_mail_password(
            ldap_server_id, email, password
        )
        return {"success": bool}


class UserPasswordCheckConsumer(BaseConsumer):
    def __init__(
        self,
        user_service: UserService,
        connection: RabbitConnection,
        rredis: Redis,
        wredis: Redis,
    ):
        super().__init__(
            "user.password_check",
            "user.password_check",
            "mapa-exchange",
            connection,
            rredis,
            wredis,
        )
        self.service = user_service

    async def process_message(self, payload: dict) -> bool:
        user_id = payload["user_id"]
        password = payload["password"]
        result = await self.service.check_password(user_id, password)
        return result
   
   
class UserPasswordUpdateConsumer(BaseConsumer):
    def __init__(
        self,
        user_service: UserService,
        connection: RabbitConnection,
        rredis: Redis,
        wredis: Redis,
    ):
        super().__init__(
            "user.password_update",
            "user.password_update",
            "mapa-exchange",
            connection,
            rredis,
            wredis,
        )
        self.service = user_service

    async def process_message(self, payload: dict) -> bool:
        user_id = payload["user_id"]
        password = payload["password"]
        await self.service.update_password(user_id, password)
        return True


class UserGetByIdConsumer(BaseConsumer):
    def __init__(
        self,
        user_service: UserService,
        connection: RabbitConnection,
        rredis: Redis,
        wredis: Redis,
    ):
        super().__init__(
            "user.get_by_id",
            "user.get_by_id",
            "mapa-exchange",
            connection,
            rredis,
            wredis,
        )
        self.service = user_service

    async def process_message(self, payload: dict) -> dict:
        user_id = payload["user_id"]
        tenant_id = payload["tenant_id"]
        fields = payload["fields"]
        user = await self.service.get_by_user_id(user_id, tenant_id, fields)
        if user is None:
            return {}
        return user.model_dump()


class UserGetByEmailConsumer(BaseConsumer):
    def __init__(
        self,
        user_service: UserService,
        connection: RabbitConnection,
        rredis: Redis,
        wredis: Redis,
    ):
        super().__init__(
            "user.get_by_email",
            "user.get_by_email",
            "mapa-exchange",
            connection,
            rredis,
            wredis,
        )
        self.service = user_service

    async def process_message(self, payload: dict) -> dict:
        email = payload["email"]
        tenant_id = payload["tenant_id"]
        user = await self.service.get_by_email(email, tenant_id)

        if user is None:
            return {}

        return user.model_dump()


class UserGetConsumer(BaseConsumer):
    def __init__(
        self,
        user_service: UserService,
        connection: RabbitConnection,
        rredis: Redis,
        wredis: Redis,
    ):
        super().__init__(
            "user.get", "user.get", "mapa-exchange", connection, rredis, wredis
        )
        self.service = user_service

    async def process_message(self, payload: dict) -> dict:
        id = payload["id"]
        tenant_id = payload.get("tenant_id")
        fields = payload.get("fields", [])
        user = await self.service.get(id, tenant_id, fields)

        if user is None:
            return {}

        return user.model_dump()


class UserFindConsumer(BaseConsumer):
    def __init__(
        self,
        user_service: UserService,
        connection: RabbitConnection,
        rredis: Redis,
        wredis: Redis,
    ):
        super().__init__(
            "user.find", "user.find", "mapa-exchange", connection, rredis, wredis
        )
        self.service = user_service

    async def process_message(self, payload: dict) -> dict:
        query_args = payload["query_args"]
        tenant_id = payload.get("tenant_id")
        result = await self.service.paging(QueryArgs(**query_args), tenant_id)
        return result.model_dump()


class UserGetScopesConsumer(BaseConsumer):
    def __init__(
        self,
        user_service: UserService,
        connection: RabbitConnection,
        rredis: Redis,
        wredis: Redis,
    ):
        super().__init__(
            "user.get_user_scopes",
            "user.get_user_scopes",
            "mapa-exchange",
            connection,
            rredis,
            wredis,
        )
        self.service = user_service

    async def process_message(self, payload: dict) -> list[str]:
        client_id = payload["client_id"]
        id = payload["id"]
        tenant_id = payload.get("tenant_id")
        result = await self.service.get_user_scopes(client_id, id, tenant_id)
        if result is None:
            return []
        return result


class UserDeleteConsumer(BaseConsumer):
    def __init__(
        self,
        user_service: UserService,
        connection: RabbitConnection,
        rredis: Redis,
        wredis: Redis,
    ):
        super().__init__(
            "user.delete", "user.delete", "mapa-exchange", connection, rredis, wredis
        )
        self.user_service = user_service

    async def process_message(self, payload: dict) -> bool:
        id = payload["id"]
        tenant_id = payload.get("tenant_id")
        result = await self.user_service.delete(id, tenant_id)
        return result
