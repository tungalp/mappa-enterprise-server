import asyncio
from base64 import b64encode
import base64
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import json
from typing import List
import jwt
import pytest
from mapa.manage.constants import GrantTypes
from mapa.sso.auth.auth_util_service import AuthUtilService
from mapa.sso.auth.forgot_password_endpoint import ForgotPasswordEndpoint
from mapa.sso.auth.login_endpoint import LoginEndpoint
from mapa.sso.auth.new_password_endpoint import NewPasswordEndpoint
from mapa.sso.auth.register_endpoint import RegisterEndpoint
from mapa.sso.constants import CodeChallengeMethods, ResponseTypes, StandardScopes
from mapa.sso.jwk.jwk_service import JwkService
from mapa.sso.oidc.end_points.authorize import AuthorizeEndpoint
from mapa.sso.oidc.end_points.end_session import EndSessionEndpoint
from mapa.sso.oidc.end_points.revocation import RevocationEndpoint
from mapa.sso.oidc.end_points.token import TokenEndpoint
from mapa.sso.oidc.token_service import TokenService
from mapa.test.base_app_fixture import BaseAppFixture
from mapa.test.base_fixture import BaseFixture
from sso.app import create_application
from httpx import AsyncClient
from ..data import instances, client_test, session_id, client_manage, client_id_manage, user_id, tenant_id


class SsoAppFixture(BaseAppFixture):
    """Test Fixture"""

    def __init__(self) -> None:
        super().__init__()

    def create_app(self):
        # FastAPI application
        self.app = create_application()

        self.auth_util_service = AuthUtilService("top_secret")
        # Test verisinin her oturumda bir kez oluşturulması gerekir.
        self.__test_data_created = False

        middleware = self.app.user_middleware[0]  # type: ignore
        session_middleware = middleware.cls(
            app=self.app, secret_key=middleware.kwargs["secret_key"])
        data = b64encode(json.dumps({
            "id": str(session_id),
            "created": datetime.utcnow().timestamp()
        }).encode("utf-8"))

        signed_session = session_middleware.signer.sign(data)
        self.session = signed_session.decode("utf-8")

        self.user_id = user_id
        self.tenant_id = tenant_id



    async def create_test_data(self, overwrite: bool = False) -> bool:
        """Veritabanında tabloları ve örnek verileri oluşturur."""

        if self.__test_data_created and not overwrite:
            return True

        async_db = self.create_db_instance(self.db_url_async_init)

        initialized = await self.create_database(async_db)
        if initialized:
            await self.grant_permissions(async_db, "mapa_test", "mapa")
            self.__test_data_created = await self.create_data(async_db, instances)

        # Token private ve public keys
        self.init_keys()
        return initialized

    def create_authorize_endpoint(self, code_challenge: str | None = None) -> AuthorizeEndpoint:
        if not code_challenge:
            code_challenge = "code_challenge_code_challenge"
        return AuthorizeEndpoint(
            client_id=str(client_manage.client_id),
            response_type=ResponseTypes.CODE,
            redirect_uri="http://localhost:33001/callback",
            scope=f"{StandardScopes.OPENID} {StandardScopes.PROFILE} {StandardScopes.EMAIL} {StandardScopes.OFFLINE_ACCESS}",
            nonce="nonce_nonce",
            state="state_state",
            code_challenge=code_challenge,
            code_challenge_method=CodeChallengeMethods.SHA256,
            audience="https://test-server/api/v1",
            language="tr"
        )

    def create_register_endpoint(self, authorize_endpoint: AuthorizeEndpoint | None = None) -> RegisterEndpoint:
        if not authorize_endpoint:
            authorize_endpoint = self.create_authorize_endpoint()
        return RegisterEndpoint(
            email="test@test_domain.com",
            password="deneme",
            name="TestName",
            surname="TestSurname",
            phone="05551112233",
            **vars(authorize_endpoint)
        )

    def create_login_endpoint(self, authorize_endpoint: AuthorizeEndpoint | None = None) -> LoginEndpoint:
        if not authorize_endpoint:
            authorize_endpoint = self.create_authorize_endpoint()
        return LoginEndpoint(
            email="admin@admin.com",
            password="admin",
            **vars(authorize_endpoint)
        )

    def create_test_login_endpoint(self) -> LoginEndpoint:
        login_endpoint = self.create_login_endpoint()
        login_endpoint.client_id = str(client_test.client_id)
        login_endpoint.redirect_uri = "http://localhost:3000"
        return login_endpoint

    def create_forgot_password_endpoint(self) -> ForgotPasswordEndpoint:
        return ForgotPasswordEndpoint(
            client_id="client_id_manage",
            email="admin@admin.com",
            state="test_state",
            lang="tr",
            audience="",
            redirect_uri="",
            scope=""
        )

    def create_new_password_endpoint(self) -> NewPasswordEndpoint:
        data = {
            "email": "admin@admin.com",
            "expired_at": (datetime.now() + timedelta(minutes=10080)).timestamp()
        }
        token = jwt.encode(data, "top_secret", "HS256")
        return NewPasswordEndpoint(
            client_id="client_id_manage",
            password='test_password',
            token=token
        )

    def create_token_auth_code_endpoint(self, code: str | None, code_verifier: str | None) -> TokenEndpoint:
        if not code:
            code = "1234567890abc"
        if not code_verifier:
            code_verifier = "2bd5W4Le5HbVb8SnFNicdiKFWeAEDE930cK1GUyRFKk-qYFChd2UTnlxtb3UuHpj"
        return TokenEndpoint(
            client_id=str(client_manage.client_id),
            client_secret=str(client_manage.client_secret),
            code=code,
            code_verifier=code_verifier,
            grant_type=GrantTypes.AUTHORIZATION_CODE,
            redirect_uri=client_manage.redirect_uris[0],
            audience="https://test-server/api/v1"
        )

    def create_end_session_endpoint(self) -> EndSessionEndpoint:
        return EndSessionEndpoint(
            id_token_hint="",
            post_logout_redirect_uri="http://localhost:33001/manage",
            state="state_state"
        )

    def create_refresh_token_endpoint(self, refresh_token: str) -> TokenEndpoint:
        return TokenEndpoint(
            client_id=client_manage.client_id,
            grant_type=GrantTypes.REFRESH_TOKEN,
            refresh_token=refresh_token
        )

    def create_revocation_endpoint(self, refresh_token: str) -> RevocationEndpoint:
        return RevocationEndpoint(
            token=refresh_token,
            token_type_hint="refresh_token"
        )

    def create_basic_auth(self, username: str, password: str) -> str:
        auth_string = f"{username}:{password}"
        return base64.b64encode(auth_string.encode("utf-8")).decode("ascii")

    def create_token(self, api_scopes: List[str] = []) -> str:
        return super().create_access_token(
            self.user_id, self.tenant_id, "client_id_manage", "http://test-api/v1", api_scopes
        )

    @asynccontextmanager
    async def client(self) -> AsyncClient:
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
async def fixture(event_loop) -> SsoAppFixture:
    """Oturum bazlı fikstür parametresi"""
    s_fixture = SsoAppFixture()
    s_fixture.drop_schema_and_migration_table("sso")
    s_fixture.create_app()
    await s_fixture.create_test_data()
    yield s_fixture

    print("Test Tamamlandı")
