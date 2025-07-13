import asyncio
from contextlib import asynccontextmanager
from uuid import UUID, uuid4

import pytest
from mapa.test.base_app_fixture import BaseAppFixture
from httpx import AsyncClient
from spatial.app import create_application

from .data import api_scopes


class SpatialAppFixture(BaseAppFixture):
    """Test Fixture"""

    def __init__(self) -> None:
        # Set all required environment variables for testing
        import os
        os.environ["MAPA_ENV"] = "DEVELOPMENT"
        # Additional ESP vars
        os.environ["ESP_HOST"] = "localhost:33001"
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
        os.environ["SERVICE_HOST"] = "http://0.0.0.0:33107"
        super().__init__()

    def create_app(self):
        # FastAPI application
        self.app = create_application()

    @asynccontextmanager  # type: ignore
    async def client(self) -> AsyncClient:  # type: ignore
        """ Http test client"""

        s_client = AsyncClient(app=self.app, base_url="http://testserver")
        token = self.create_access_token(
            uuid4(), UUID(self.tenant_id), "client_id_spatial", "http://test.application", api_scopes)
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
async def fixture(event_loop) -> SpatialAppFixture:  # type: ignore
    """Oturum bazlı fikstür parametresi"""
    s_fixture = SpatialAppFixture()
    s_fixture.create_app()
    s_fixture.init_keys()
    yield s_fixture

    print("Test Tamamlandı")
