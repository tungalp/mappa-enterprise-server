import asyncio
from contextlib import asynccontextmanager
from typing import List
import pytest
from httpx import AsyncClient
from mapa.test.base_app_fixture import BaseAppFixture
from application.app import create_application
from mapa.application.app.app_model import CreateApp
from mapa.application.content_page.content_page_model import CreateContentPage
from nanoid import generate
from uuid import UUID, uuid4
from ..data import tenant_id, api_scopes

tenant_id = "10a2238f-4d1e-4626-9f3c-799d3ef5e96d"

class ApplicationAppFixture(BaseAppFixture):
    """Test Fixture"""

    def __init__(self) -> None:
        # Set all required environment variables for testing
        import os
        os.environ["MAPA_ENV"] = "DEVELOPMENT"
        os.environ["SKIP_MIGRATIONS"] = "true"  # Skip migrations in test environment
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
        
        # FastAPI application with fixed migration path
        app = create_application()
        super().__init__()
        self.app = app

    @asynccontextmanager
    async def client(self) -> AsyncClient:
        """ Http test client"""

        s_client = AsyncClient(app=self.app, base_url="http://testserver")
        token = self.create_access_token(
            uuid4(), UUID(tenant_id), "client_id_application", "http://test.application", api_scopes)
        s_client.headers.update({
           "Authorization": f"Bearer {token}"
        })
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
async def fixture(event_loop) -> ApplicationAppFixture:
    """Oturum bazlı fikstür parametresi"""
    s_fixture = ApplicationAppFixture()
    s_fixture.init_keys()
    yield s_fixture

    print("Test Tamamlandı")

