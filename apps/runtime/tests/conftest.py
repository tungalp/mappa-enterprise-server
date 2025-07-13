import asyncio
from typing import Any, AsyncGenerator, List
import uuid
import pytest
from contextlib import asynccontextmanager
from sqlalchemy import text
from mapa.test.base_app_fixture import BaseAppFixture
from runtime.app import create_application
from httpx import AsyncClient



class RuntimeAppFixture(BaseAppFixture):
    """Test Fixture"""

    # Admin user ve tenant
    user_id = uuid.UUID("7175e67d-0ddc-4c96-a167-c3f3ef72de5a")
    tenant_id = uuid.UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d")
    client_id = "client_id_test"
    audience = "http://client_id_test/api"
    runtime_url = "http://localhost:33108"

    def __init__(self) -> None:
        # FastAPI application
        app = create_application()
        super().__init__(app)

        # Test verisinin her oturumda bir kez oluşturulması gerekir.
        self.__test_data_created = False

    async def create_test_data(self, overwrite: bool = False) -> bool:
        """Veritabanında tabloları ve örnek verileri oluşturur."""

        if self.__test_data_created and not overwrite:
            return True

        async_db = self.create_db_instance(self.db_url_async_init)
        initialized = async_db is not None
        # if initialized:
        #     await self.grant_permissions(async_db, "mapa_test", "mapa")
        #     instances = []
        #     try:
        #         async with async_db.session() as session:
        #             await session.commit()

        #         self.__test_data_created = await self.create_data(async_db, instances)

        #     except Exception as ex:
        #         print("hata ", ex)

        return initialized

    @asynccontextmanager # type: ignore
    async def client(self) -> AsyncClient:  # type: ignore
        """ Http test client"""

        s_client = AsyncClient(app=self.app, base_url="http://testserver")
        yield s_client # type: ignore


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
async def fixture(event_loop) -> AsyncGenerator[RuntimeAppFixture, Any]:
    """Oturum bazlı fikstür parametresi"""
    s_fixture = RuntimeAppFixture()
    yield s_fixture

    print("Test Tamamlandı")
