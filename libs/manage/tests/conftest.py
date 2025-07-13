import asyncio
import secrets
import string
import pytest
from mapa.test.base_fixture import BaseFixture
from mapa.manage.client.client_model import CreateClient
from mapa.manage.api.api_model import CreateApi
from mapa.manage.api_scope.api_scope_model import CreateApiScope
from mapa.manage.client_api_scope.client_api_scope_model import CreateClientApiScope
from mapa.manage.client_api.client_api_model import CreateClientApi
from nanoid import generate
from mapa.manage.constants import ApplicationTypes
from uuid import UUID, uuid4
from mapa.manage.invitation.invitation_model import CreateInvitation
from .data import instances, session_id, client_manage, user_id, audience, nonce,tenant_id

class ManageFixture(BaseFixture):
    """Test Fixture"""

    def __init__(self) -> None:
        super().__init__()
        # Test verisinin her oturumda bir kez oluşturulması gerekir.
        self.__test_data_created = False
        self.api_host = "http://127.0.0.1:33101"
        self.app_host = "http://127.0.0.1:33001"
        self.jwt_secret = "top_secret"
        self.jwt_secret = "top_secret"
        self.client_id = "client_id_manage"
        self.session_timeout = 10800
        self.session_id = session_id
        self.client_manage = client_manage
        self.user_id = user_id
        self.audience = audience
        self.nonce = nonce
        self.tenant_id = tenant_id

    async def create_test_data(self) -> bool:
        """Veritabanında tabloları ve örnek verileri oluşturur."""

        if self.__test_data_created:
            return True

        async_db = self.create_db_instance(self.db_url_async_init)

        initialized = await self.create_database(async_db)
        self.__test_data_created = True

        if initialized:
            await self.grant_permissions(async_db, "mapa_test", "mapa", "manage")
            self.__test_data_created = await self.create_data(async_db, instances)

        return initialized


@pytest.fixture(scope="session")
def event_loop():
    """Async test metodları için default event loop"""

    try:
        loop = asyncio.get_running_loop()
    except Exception:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def fixture(event_loop) -> ManageFixture:  # type: ignore
    s_fixture = ManageFixture()
    await s_fixture.create_test_data()
    yield s_fixture

    print("Test Tamamlandı")


def generate_client() -> CreateClient:
    return CreateClient(
        name="client_test_"+generate(size=4),
        client_id=generate(
            size=32),
        client_secret=generate(size=64),
        grant_types=["authorization_code"],
        application_type=ApplicationTypes.WEB,
        logo_url="https://www.mapa.com.tr/application/views/islemgis/layouts/images/logo-colored.png")  # type: ignore


def generate_api() -> CreateApi:
    return CreateApi(name="test"+generate(size=4), identifier="https://test.api"+generate(size=4))


def generate_api_scope(api_id: UUID = uuid4()) -> CreateApiScope:
    return CreateApiScope(name=("test:test"+str(api_id)), description="test scope", api_id=api_id)


def generate_client_api(client_id: UUID = uuid4(), api_id: UUID = uuid4()) -> CreateClientApi:
    return CreateClientApi(client_id=client_id, api_id=api_id)


def generate_client_api_scope(client_api_id: UUID = uuid4(), api_scope_id: UUID = uuid4()) -> CreateClientApiScope:
    return CreateClientApiScope(client_api_id=client_api_id, api_scope_id=api_scope_id)

