from datetime import datetime, timedelta
from random import random
import types
import pytest
from mapa.sso.auth.auth_service import AuthService
from mapa.sso.auth.consent_endpoint import ConsentEndpoint
from mapa.sso.auth.consent_result import ConsentResult
from mapa.sso.auth.login_endpoint import LoginEndpoint
from mapa.sso.auth.login_result import LoginResult
from mapa.sso.auth.new_password_endpoint import NewPasswordEndpoint
from mapa.sso.auth.register_endpoint import RegisterEndpoint
from mapa.sso.authorization_code.authorization_code_model import CreateAuthorizationCode, UpdateAuthorizationCode
from mapa.sso.authorization_code.authorization_code_service import AuthorizatioCodeService
from mapa.manage.client.client_service import ClientService
from mapa.sso.consent.consent_service import ConsentService
from mapa.sso.oidc.validation.authorize_endpoint_validator import AuthorizeEndPointValidator
from mapa.manage.user.user_service import UserService
from mapa.manage.tenant.tenant_service import TenantService
from mapa.manage.tenant_user.tenant_user_service import TenantUserService
from mapa.sso.user_session.user_session_service import UserSessionService
from .conftest import SsoFixture


async def create_service(fixture: SsoFixture) -> AuthorizatioCodeService:
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True

    async_db = fixture.create_db_instance(fixture.db_url_async)

    return AuthorizatioCodeService(async_db=async_db)


@pytest.mark.asyncio
async def test_create_service(fixture: SsoFixture):
    """Service"""
    
    service: AuthorizatioCodeService = await create_service(fixture)
    assert service is not None

    
@pytest.mark.asyncio
async def test_create_update_code(fixture: SsoFixture):
    """Service"""
    
    service: AuthorizatioCodeService = await create_service(fixture)
    assert service is not None
    
    authorization_code = await service.create(CreateAuthorizationCode(
        user_session_id=fixture.session_id,
        user_id=fixture.user_id,
        client_id=fixture.client_id,
        audience=fixture.audience,
        nonce=fixture.nonce,
        code_challenge="abcdefh",
        code_challenge_method="S256",
        redirect_uri=fixture.client_manage.redirect_uris[0],
        scopes=["openid", "profile", "email", "offline_access"],
        code=service.generate_code(),
        created_at=datetime.now(),
        expired_at=datetime.now() + timedelta(minutes=10)
    ), fixture.tenant_id)
    assert authorization_code is not None
    
    updated_auth_code = await service.update(authorization_code.id, UpdateAuthorizationCode(used=True))
    
    assert updated_auth_code.used == True
