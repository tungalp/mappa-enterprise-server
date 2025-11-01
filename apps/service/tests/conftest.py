import asyncio
from typing import List
import uuid
import pytest
from contextlib import asynccontextmanager
from sqlalchemy import text
from mapa.test.base_app_fixture import BaseAppFixture
from service.app import create_application
from httpx import AsyncClient

from tests.data_adhoc_kisi_sql import create_kisi_model
from .data import instances as base_instances
from .data_adhoc_kisi import instances as adhoc_kisi_instances
from .data_adhoc_lookup import instances as lookup_instances
from .data_adhoc_ora import instances as adhoc_ora_instances
from .data_adhoc_crud import instances as adhoc_crud_instances
from .data_adhoc_nodes import instances as adhoc_nodes_instances
from .data_http import instances as http_instances
from .data_http2 import instances as http2_instances
from .data_soap import instances as soap_instances
from .data_spatial import instances as spatial_instances
from .data_function import instances as function_instances

class ServiceAppFixture(BaseAppFixture):
    """Test Fixture"""

    # Admin user ve tenant
    user_id = uuid.UUID("7175e67d-0ddc-4c96-a167-c3f3ef72de5a")
    tenant_id = uuid.UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d")
    client_id = "client_id_test"
    audience = "http://client_id_test/api"
    gw_db_url = "postgresql+psycopg2://postgres:postgres@db/esp_test"

    def __init__(self) -> None:
        # Set all required environment variables for testing
        import os
        os.environ["MAPA_ENV"] = "DEVELOPMENT"
        # Additional ESP vars
        os.environ["MANAGE_HOST"] = "localhost:33001"
        os.environ["JWT_SECRET"] = "test_jwt_secret"
        os.environ["SCHEME"] = "http"
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
        os.environ["REDIS_PREFIX"] = "mapa-manage-redis-test"
        # Mail vars
        os.environ["MAIL_SMTP"] = "smtp.example.com"
        os.environ["MAIL_PORT"] = "587"
        os.environ["MAIL_USER_NAME"] = "test@example.com"
        os.environ["MAIL_PASSWORD"] = "test_password"
        os.environ["MAIL_METHOD"] = "STARTTLS"
        os.environ["MAIL_SUBJECT"] = "Test Subject"
        os.environ["MAIL_HEADER"] = "Test Header"
        os.environ["MAIL_HEADER_EN"] = "Test Header EN"

        super().__init__()

        # Test verisinin her oturumda bir kez oluşturulması gerekir.
        self.__test_data_created = False

    def create_app(self):
        # FastAPI application
        self.app = create_application()
    
    async def create_test_data(self, overwrite: bool = False) -> bool:
        """Veritabanında tabloları ve örnek verileri oluşturur."""

        if self.__test_data_created and not overwrite:
            return True

        async_db = self.create_db_instance(self.db_url_async_init)
        # Şema ve veritabanı oluşturulur.
        # await self.create_schema(async_db, "gateway")
        # initialized = await self.create_database(async_db)
        initialized = async_db is not None
        if initialized:
            await self.grant_permissions(async_db, "mapa_test", "mapa")
            instances = adhoc_kisi_instances + lookup_instances + adhoc_ora_instances + adhoc_crud_instances + \
                adhoc_nodes_instances + http_instances + \
                http2_instances + soap_instances + spatial_instances + function_instances
            try:
                async with async_db.session() as session:
                    await session.execute(text("truncate table gateway.gateway_api cascade"))
                    await session.execute(text("truncate table gateway.route cascade"))
                    await session.execute(text("truncate table gateway.integration cascade"))
                    await session.execute(text("truncate table gateway.parameter_mapping cascade"))
                    await session.execute(text("truncate table gateway.connection_info cascade"))
                    await session.execute(text("truncate table gateway.context_var cascade"))
                    await session.commit()

                # Temel veriler
                try:
                    await self.create_data(async_db, base_instances)
                except Exception as ex:
                    print("hata ", ex)

                # Kisi modeli
                try:
                    await create_kisi_model(async_db)
                except Exception as ex:
                    print("hata ", ex)

                self.__test_data_created = await self.create_data(async_db, instances)

            except Exception as ex:
                print("hata ", ex)

        return initialized

    def create_token(self, api_scopes: List[str]) -> str:
        # Access Token
        token = self.create_access_token(
            self.user_id, self.tenant_id, self.client_id, self.audience, api_scopes)
        return token

    @asynccontextmanager
    async def client(self) -> AsyncClient:  # type: ignore
        """ Http test client"""

        s_client = AsyncClient(app=self.app, base_url="http://testserver")
        yield s_client


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
async def fixture(event_loop) -> ServiceAppFixture:
    """Oturum bazlı fikstür parametresi"""
    s_fixture = ServiceAppFixture()
    s_fixture.drop_schema_and_migration_table("adhoc")

    s_fixture.create_app()
    await s_fixture.create_test_data()
    s_fixture.init_keys()
    yield s_fixture

    print("Test Tamamlandı")
