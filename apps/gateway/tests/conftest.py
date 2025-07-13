import asyncio
from contextlib import asynccontextmanager
import uuid
import pytest
from httpx import AsyncClient
from mapa.test.base_app_fixture import BaseAppFixture
from gateway.app import create_application
from uuid import UUID, uuid4
from .data import instances, api_scopes


class GatewayAppFixture(BaseAppFixture):
    """Test Fixture"""

    def __init__(self) -> None:
        # Set all required environment variables for testing
        import os
        os.environ["MAPA_ENV"] = "DEVELOPMENT"
        # RabbitMQ vars (even though dev config has defaults, strict mode requires them)
        os.environ["RABBIT_V_HOST"] = "/"
        os.environ["RABBIT_HOST"] = "localhost"
        os.environ["RABBIT_PORT"] = "5672"
        os.environ["RABBIT_USERNAME"] = "mapa"
        os.environ["RABBIT_PASSWORD"] = "mapa"
        os.environ["RABBIT_EXCHANGE_NAME"] = "mapa-exchange"
        # Database vars (even though dev config has defaults, strict mode requires them)
        os.environ["DB_USER"] = "mapa"
        os.environ["DB_PASSWORD"] = "12345Abc."
        os.environ["DB_HOST"] = "localhost"
        os.environ["DB_NAME"] = "mapa_test"
        os.environ["MIG_USER"] = "postgres"
        os.environ["MIG_PASSWORD"] = "postgres"
        # Redis vars
        os.environ["REDIS_HOST"] = "localhost"
        os.environ["REDIS_WRITE_PORT"] = "6379"
        os.environ["REDIS_READ_PORT"] = "6379"
        os.environ["REDIS_DB"] = "0"
        os.environ["REDIS_PASSWORD"] = "mapa"
        os.environ["REDIS_PREFIX"] = "mapa-gateway-redis-test"
        
        super().__init__()

    def create_app(self):
        # FastAPI application
        self.app = create_application()

    @asynccontextmanager  # type: ignore
    async def client(self) -> AsyncClient:  # type: ignore
        """ Http test client"""

        s_client = AsyncClient(app=self.app, base_url="http://testserver")
        token = self.create_access_token(
            uuid4(), UUID(self.tenant_id), "client_id_gateway", "http://test.application", api_scopes)
        s_client.headers.update({
            "Authorization": f"Bearer {token}"
        })
        yield s_client

    async def create_test_data(self, overwrite: bool = False) -> bool:
        """Veritabanında tabloları ve örnek verileri oluşturur."""

        async_db = self.create_db_instance(self.db_url_async_init)
        initialized = async_db is not None
        if initialized:
            try:
                await self.create_data(async_db, instances)
            except Exception as ex:
                print("hata ", ex)

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
async def fixture(event_loop) -> GatewayAppFixture:  # type: ignore
    """Test bazlı fikstür parametresi"""
    s_fixture = GatewayAppFixture()
    s_fixture.drop_schema_and_migration_table("gateway", ["outbox_status_enum_gateway"])
    
    s_fixture.create_app()
    await s_fixture.create_test_data()
    s_fixture.init_keys()
    yield s_fixture

    print("Test Tamamlandı")
