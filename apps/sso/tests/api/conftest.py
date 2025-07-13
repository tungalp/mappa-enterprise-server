import asyncio
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import jwt
import pytest
from mapa.sso.auth.consent_endpoint import ConsentEndpoint
from mapa.sso.auth.login_endpoint import LoginEndpoint
from mapa.sso.auth.new_password_endpoint import NewPasswordEndpoint
from mapa.sso.auth.register_endpoint import RegisterEndpoint
from mapa.sso.constants import CodeChallengeMethods, ResponseTypes, StandardScopes
from mapa.sso.oidc.end_points.authorize import AuthorizeEndpoint
from mapa.sso.oidc.end_points.end_session import EndSessionEndpoint
from mapa.sso.oidc.end_points.revocation import RevocationEndpoint
from mapa.sso.oidc.end_points.token import TokenEndpoint
from mapa.test.base_fixture import BaseFixture
from ..data import instances, session_id, client_manage, user_id, audience, nonce, tenant_id
from mapa.manage.constants import GrantTypes


class SsoFixture(BaseFixture):
    """Test Fixture"""

    def __init__(self) -> None:
        super().__init__()
        # Test verisinin her oturumda bir kez oluşturulması gerekir.
        self.__test_data_created = False
        self.issuer = 'http://127.0.0.1:33100'
        self.api_host = "http://127.0.0.1:33100"
        self.app_host = "http://127.0.0.1:33000"
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
            await self.grant_permissions(async_db, "mapa_test", "mapa", "sso")
            await self.grant_permissions(async_db, "mapa_test", "mapa", "manage")
            self.__test_data_created = await self.create_data(async_db, instances)

        return initialized

    def create_authorize_endpoint(self) -> AuthorizeEndpoint:
        return AuthorizeEndpoint(
            client_id=self.client_id,
            response_type=ResponseTypes.CODE,
            redirect_uri="http://localhost:33001/manage/callback",
            scope=f"{StandardScopes.OPENID} {StandardScopes.PROFILE} {StandardScopes.EMAIL} {StandardScopes.OFFLINE_ACCESS}",
            nonce=nonce,
            state="state_state",
            code_challenge="code_challenge_code_challenge",
            code_challenge_method=CodeChallengeMethods.SHA256,
            audience="https://test-server/api/v1",
            language="tr"
        )

    def create_register_endpoint(self) -> RegisterEndpoint:
        authorize_endpoint = self.create_authorize_endpoint()
        return RegisterEndpoint(
            email="test@test_domain.com",
            password="deneme",
            name="TestName",
            surname="TestSurname",
            phone="05551112233",
            **vars(authorize_endpoint)
        )

    def create_login_endpoint(self) -> LoginEndpoint:
        authorize_endpoint = self.create_authorize_endpoint()
        return LoginEndpoint(
            email="admin@admin.com",
            password="admin",
            **vars(authorize_endpoint)
        )

    def create_consent_endpoint(self, accepted: bool) -> ConsentEndpoint:
        authorize_endpoint = self.create_authorize_endpoint()
        return ConsentEndpoint(
            accepted=accepted,
            **vars(authorize_endpoint)
        )

    def create_new_password_endpoint(self, email: str) -> NewPasswordEndpoint:
        data = {
            "email": email,
            "expired_at": (datetime.now() + timedelta(minutes=10080)).timestamp()
        }
        token = jwt.encode(data, self.jwt_secret, "HS256")
        return NewPasswordEndpoint(
            client_id=self.client_id,
            password='test_password',
            token=token
        )

    def create_token_auth_code_endpoint(self) -> TokenEndpoint:
        return TokenEndpoint(
            client_id=str(client_manage.client_id),
            code="1234567890abc",
            code_verifier="2bd5W4Le5HbVb8SnFNicdiKFWeAEDE930cK1GUyRFKk-qYFChd2UTnlxtb3UuHpj",
            grant_type=GrantTypes.AUTHORIZATION_CODE,
            redirect_uri=client_manage.redirect_uris[0],
            audience=audience
        )

    def create_end_session_endpoint(self) -> EndSessionEndpoint:
        return EndSessionEndpoint(
            id_token_hint="",
            post_logout_redirect_uri="http://localhost:33001/manage",
            state="state_state"
        )

    def create_refresh_token_endpoint(self, refresh_token: str) -> TokenEndpoint:
        return TokenEndpoint(
            client_id=str(client_manage.client_id),
            grant_type=GrantTypes.REFRESH_TOKEN,
            refresh_token=refresh_token,
        )

    def create_revocation_endpoint(self, refresh_token: str) -> RevocationEndpoint:
        return RevocationEndpoint(
            token=refresh_token,
            token_type_hint="refresh_token",
            client_id=str(client_manage.client_id),
            client_secret=str(client_manage.client_secret)
        )

    def generate_new_session_id(self):
        return uuid4()


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
async def fixture(event_loop) -> SsoFixture: # type: ignore 
    """Oturum bazlı fikstür parametresi_
    """
    yield SsoFixture()


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
            await self.grant_permissions(async_db, "mapa_test", "mapa", "manage")
            await self.grant_permissions(async_db, "mapa_test", "mapa", "sso")
            # self.__test_data_created = await self.create_data(async_db, instances)

        return initialized
