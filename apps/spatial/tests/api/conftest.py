
import asyncio

import pytest
from mapa.test.base_fixture import BaseFixture


class SpatialFixture(BaseFixture):
    """Test Fixture"""

    def __init__(self) -> None:
        # Test verisinin her oturumda bir kez oluşturulması gerekir.
        self.__test_data_created = False
        self.config = {
            "api_host": "http://0.0.0.0:33107",
            "app_host": "http://0.0.0.0:33007",
            "secret": "top_secret"
        }

    async def create_test_data(self) -> bool:
        """Veritabanında tabloları ve örnek verileri oluşturur."""

        if self.__test_data_created:
            return True

        async_db = self.create_db_instance(self.db_url_async_init)

        initialized = await self.create_database(async_db)
        self.__test_data_created = True

        if initialized:
            await self.grant_permissions(async_db, "mapa_test", "mapa", "spatial")
            await self.grant_permissions(async_db, "mapa_test", "mapa", "manage")
            await self.grant_permissions(async_db, "mapa_test", "mapa", "gateway")
            # self.__test_data_created = await self.create_data(async_db, instances)

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
async def fixture(event_loop) -> SpatialFixture:  # type: ignore
    """Oturum bazlı fikstür parametresi_
    """
    yield SpatialFixture()


class GatewayFixture(BaseFixture):
    """Test Fixture"""

    def __init__(self) -> None:
        super().__init__()
        # Test verisinin her oturumda bir kez oluşturulması gerekir.
        self.__test_data_created = False
        self.config = {
            "api_host": "http://0.0.0.0:33104",
            "app_host": "http://0.0.0.0:33004",
            "secret": "top_secret"
        }

    async def create_test_data(self) -> bool:
        """Veritabanında tabloları ve örnek verileri oluşturur."""

        if self.__test_data_created:
            return True

        async_db = self.create_db_instance(self.db_url_async_init)

        initialized = await self.create_database(async_db)
        self.__test_data_created = True

        if initialized:
            await self.grant_permissions(async_db, "mapa_test", "mapa", "spatial")
            await self.grant_permissions(async_db, "mapa_test", "mapa", "manage")
            await self.grant_permissions(async_db, "mapa_test", "mapa", "gateway")
            # self.__test_data_created = await self.create_data(async_db, instances)

        return initialized


class ManageFixture(BaseFixture):
    """Test Fixture"""

    def __init__(self) -> None:
        super().__init__()
        # Test verisinin her oturumda bir kez oluşturulması gerekir.
        self.__test_data_created = False
        self.config = {
            "api_host": "http://0.0.0.0:33101",
            "app_host": "http://0.0.0.0:33001",
            "secret": "top_secret"
        }

    async def create_test_data(self) -> bool:
        """Veritabanında tabloları ve örnek verileri oluşturur."""

        if self.__test_data_created:
            return True

        async_db = self.create_db_instance(self.db_url_async_init)

        initialized = await self.create_database(async_db)
        self.__test_data_created = True

        if initialized:
            await self.grant_permissions(async_db, "mapa_test", "mapa", "spatial")
            await self.grant_permissions(async_db, "mapa_test", "mapa", "manage")
            await self.grant_permissions(async_db, "mapa_test", "mapa", "gateway")
            # self.__test_data_created = await self.create_data(async_db, instances)

        return initialized
