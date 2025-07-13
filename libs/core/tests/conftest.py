from typing import AsyncGenerator
from mapa.core.data.async_db import AsyncDatabase
from mapa.test.base_fixture import BaseFixture
from tests.data.data import instances
import asyncio
import pytest


class CoreFixture(BaseFixture):
    """Test Fixture"""

    def __init__(self) -> None:
        super().__init__()
        # Test verisinin her oturumda bir kez oluşturulması gerekir.
        self.__test_data_created = False

    async def create_test_data(self) -> bool:
        """Veritabanında tabloları ve örnek verileri oluşturur."""

        if self.__test_data_created:
            return True

        async_db = self.create_db_instance(self.db_url_async_init)

        initialized = await self.create_database(async_db)
        if initialized:
            await self.grant_permissions(async_db, "mapa_test", "mapa")
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
async def fixture(event_loop) -> AsyncGenerator[CoreFixture, None]:
    """Oturum bazlı fikstür parametresi_
    """
    yield CoreFixture()
