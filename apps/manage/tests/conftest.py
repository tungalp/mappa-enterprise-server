import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
import uuid
import pytest
from httpx import AsyncClient
from mapa.manage.constants import ApplicationTypes
from mapa.test.base_app_fixture import BaseAppFixture
from manage.app import create_application
from mapa.manage.role.role_model import CreateRole
from mapa.manage.role_api_scope.role_api_scope_model import CreateRoleApiScope
from mapa.manage.role_user.role_user_model import CreateRoleUser
from mapa.manage.profile_adaptor.profile_adaptor_model import CreateProfileAdaptor
from mapa.manage.user.user_model import CreateUser, User
from mapa.manage.client.client_model import CreateClient
from mapa.manage.api.api_model import CreateApi
from mapa.manage.api_scope.api_scope_model import CreateApiScope
from mapa.manage.client_api_scope.client_api_scope_model import CreateClientApiScope
from mapa.manage.client_api.client_api_model import CreateClientApi
from nanoid import generate
from uuid import UUID, uuid4
from .data import api_scopes

tenant_id = "10a2238f-4d1e-4626-9f3c-799d3ef5e96d"

class ManageAppFixture(BaseAppFixture):
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
        
        super().__init__()
        
        self.user_id = uuid.UUID("7175e67d-0ddc-4c96-a167-c3f3ef72de5a")
        self.tenant_id = uuid.UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d")

    def create_app(self):
        # FastAPI application
        self.app = create_application()

    async def create_test_data(self, overwrite: bool = False) -> bool:
        """Veritabanında tabloları ve örnek verileri oluşturur."""
        async_db = self.create_db_instance(self.db_url_async_init)
        initialized = async_db is not None
        if initialized:
            try:
                # Import instances from data.py (currently empty list)
                from .data import instances
                await self.create_data(async_db, instances)
            except Exception as ex:
                print("hata ", ex)
        return initialized

    @asynccontextmanager
    async def client(self) -> AsyncClient:
        """ Http test client"""

        s_client = AsyncClient(app=self.app, base_url="http://testserver")
        token = self.create_access_token(
            uuid4(), UUID(tenant_id), "client_id_manage", "http://test.application", api_scopes)
        s_client.headers.update({
           "Authorization": f"Bearer {token}"
        })
        yield s_client

    def create_token(self) -> str:
        return super().create_access_token(
            self.user_id, self.tenant_id, "client_id_manage", "http://test-api/v1", api_scopes
        )

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
async def fixture(event_loop) -> ManageAppFixture:
    """Oturum bazlı fikstür parametresi"""
    s_fixture = ManageAppFixture()
    s_fixture.drop_schema_and_migration_table("manage")
    
    s_fixture.create_app()
    await s_fixture.create_test_data()
    s_fixture.init_keys()
    yield s_fixture

    print("Test Tamamlandı")


def generate_client() -> CreateClient:
    return CreateClient(
        name="client_test_"+generate(size=4),
        grant_types=["authorization_code"],
        application_type=ApplicationTypes.WEB,
        logo_url="https://www.islem.com.tr/application/views/islemgis/layouts/images/logo-colored.png")  # type: ignore


def generate_api() -> CreateApi:
    return CreateApi(name=generate(size=4) + "test", identifier="https://test.api"+generate(size=4))


def generate_api_scope(api_id: UUID = uuid4()) -> CreateApiScope:
    return CreateApiScope(name="test:test"+generate(size=4), description="test scope"+generate(size=4), api_id=api_id)


def generate_client_api(client_id: UUID = uuid4(), api_id: UUID = uuid4()) -> CreateClientApi:
    return CreateClientApi(client_id=client_id, api_id=api_id)


def generate_client_api_scope(client_api_id: UUID = uuid4(), api_scope_id: UUID = uuid4()) -> CreateClientApiScope:
    return CreateClientApiScope(client_api_id=client_api_id, api_scope_id=api_scope_id)


def generate_role() -> CreateRole:
    return CreateRole(
        name="test_servis_name" + generate(size=4),
        description="test_servis_desc" + generate(size=4))


def generate_user() -> CreateUser:
    return CreateUser(
        name="service user1",
        surname="service username1",
        email=generate(size=4) + "test_service_user1@gmail.com",
        subject_id=generate(size=4) + "111",
        phone="111",
        password="111")


def generate_role_api_scope(role_id: UUID = uuid4(), api_scope_id: UUID = uuid4()) -> CreateRoleApiScope:
    return CreateRoleApiScope(role_id=role_id, api_scope_id=api_scope_id)

def generate_profile_adaptor() -> CreateProfileAdaptor:
    return CreateProfileAdaptor(
        user_info_endpoint="https://tekliurl.com",
        user_info_list_endpoint="https://cokluurl.com")

def generate_role_user(role_id: UUID = uuid4(), user_id: UUID = uuid4()) -> CreateRoleUser:
    return CreateRoleUser(
        expired_at=datetime.now(),
        user_id=user_id,
        role_id=role_id)
