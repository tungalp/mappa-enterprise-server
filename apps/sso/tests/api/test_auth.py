from datetime import datetime, timedelta
from random import random
import types
import pytest
from mapa.manage.invitation.invitation_model import CreateInvitation
from mapa.manage.invitation.invitation_service import InvitationService
from mapa.manage.organization_client.organization_client_service import OrganizationClientService
from mapa.manage.organization_user.organization_user_service import OrganizationUserService
from mapa.manage.organization_type.organization_type_service import OrganizationTypeService
from mapa.manage.organization.organization_service import OrganizationService
from mapa.manage.tenant_client.tenant_client_service import TenantClientService
from mapa.sso.auth.auth_service import AuthService
from mapa.sso.auth.auth_util_service import AuthUtilService
from mapa.sso.auth.consent_endpoint import ConsentEndpoint
from mapa.sso.auth.consent_result import ConsentResult
from mapa.sso.auth.login_endpoint import LoginEndpoint
from mapa.sso.auth.login_result import LoginResult
from mapa.sso.auth.new_password_endpoint import NewPasswordEndpoint
from mapa.sso.auth.register_endpoint import RegisterEndpoint
from mapa.manage.client.client_service import ClientService
from mapa.manage.api.api_service import ApiService
from mapa.sso.consent.consent_service import ConsentService
from mapa.sso.oidc.validation.authorize_endpoint_validator import AuthorizeEndPointValidator
from mapa.manage.user.user_service import UserService
from mapa.manage.tenant.tenant_service import TenantService
from mapa.manage.tenant_user.tenant_user_service import TenantUserService
from mapa.sso.user_session.user_session_service import UserSessionService
from mapa.sso.user_session_client.user_session_client_service import UserSessionClientService
from .conftest import SsoFixture


async def create_service(fixture: SsoFixture) -> AuthService:
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True

    async_db = fixture.create_db_instance(fixture.db_url_async)
    tenant_client_service = TenantClientService(async_db)

    client_service = ClientService(async_db, tenant_client_service)
    api_service = ApiService(async_db)
    organization_client_service = OrganizationClientService(async_db)
    organization_service = OrganizationService(async_db,organization_client_service)
    user_service = UserService(async_db,api_service,organization_service)
    tenant_service = TenantService(async_db)
    tenant_user_service = TenantUserService(async_db)
    user_session_service = UserSessionService(async_db)
    user_session_client_service = UserSessionClientService(async_db)
    consent_service = ConsentService(async_db)
    authorize_endpoint_validator = AuthorizeEndPointValidator(
        client_service,
        user_session_service)
    invitation_service = InvitationService(async_db)
    organization_type_service = OrganizationTypeService(async_db)
    organization_user_service = OrganizationUserService(async_db)

    return AuthService(
        fixture.jwt_secret,
        fixture.session_timeout,
        authorize_endpoint_validator,
        user_service,
        client_service,
        tenant_service,
        tenant_user_service,
        user_session_service,
        user_session_client_service,
        consent_service,
        invitation_service,
        organization_service,
        organization_type_service,
        organization_user_service
    )


@pytest.mark.asyncio
async def test_create_service(fixture: SsoFixture):
    """Service"""

    service: AuthService = await create_service(fixture)
    assert service is not None


@pytest.mark.asyncio
async def test_register_new(fixture: SsoFixture):
    """Service"""

    service: AuthService = await create_service(fixture)
    assert service is not None

    register_endpoint: RegisterEndpoint = fixture.create_register_endpoint()
    # Test endpoint yapısındeki email değiştirilerek yeni bir kullanıcı oluşturulur.
    register_endpoint.email = f"{int(random()*1000)}_{register_endpoint.email}"

    tenant_user, user_session, auth_request = await service.register(fixture.session_id, register_endpoint)
    assert tenant_user is not None
    assert user_session is not None
    assert auth_request is not None


@pytest.mark.asyncio
async def test_register_existing(fixture: SsoFixture):
    """Service"""

    service: AuthService = await create_service(fixture)
    assert service is not None

    register_endpoint: RegisterEndpoint = fixture.create_register_endpoint()
    register_endpoint.email = "admin@admin.com"

    # Mevcut kullanıcı yeniden oluşturulmaya çalışılır. ValueError hatası oluşması beklenir.
    with pytest.raises(ValueError, match=r"already"):
        tenant_user, user_session, auth_request = await service.register(fixture.session_id, register_endpoint)


@pytest.mark.asyncio
async def test_login_success(fixture: SsoFixture):
    """Service"""

    service: AuthService = await create_service(fixture)
    assert service is not None

    login_endpoint: LoginEndpoint = fixture.create_login_endpoint()
    session_id = fixture.generate_new_session_id()

    tenant_id, user_session, auth_request = await service.login(session_id, login_endpoint)
    assert user_session is not None and auth_request is not None
    assert user_session.authenticated


@pytest.mark.asyncio
async def test_login_fail_not_found(fixture: SsoFixture):
    """Service"""

    service: AuthService = await create_service(fixture)
    assert service is not None

    login_endpoint: LoginEndpoint = fixture.create_login_endpoint()
    session_id = fixture.generate_new_session_id()

    # Kullanıcı bulanamadı hatası alınması beklenir
    login_endpoint.email = "not_found@exception.com"
    with pytest.raises(ValueError, match=r"not found"):
        user_session, auth_request = await service.login(session_id, login_endpoint)


@pytest.mark.asyncio
async def test_login_fail_password_not_match(fixture: SsoFixture):
    """Service"""

    service: AuthService = await create_service(fixture)
    assert service is not None

    login_endpoint: LoginEndpoint = fixture.create_login_endpoint()
    session_id = fixture.generate_new_session_id()

    # Şifre hatası alınması beklenir
    login_endpoint.password = "not_match_password"
    with pytest.raises(ValueError, match=r"match"):
        user_session, auth_request = await service.login(session_id, login_endpoint)


@pytest.mark.asyncio
async def test_consent_accepted(fixture: SsoFixture):
    """Service"""

    service: AuthService = await create_service(fixture)
    assert service is not None

    # Kullanıcı sisteme giriş yapar
    login_endpoint: LoginEndpoint = fixture.create_login_endpoint()
    session_id = fixture.generate_new_session_id()

    tenant_id, user_session, auth_request = await service.login(session_id, login_endpoint)
    assert user_session is not None

    # Onay bilgileri oluşturulur. Onay talep edilen izinler verilir
    consent_endpoint: ConsentEndpoint = fixture.create_consent_endpoint(
        accepted=True)
    consent, auth_request = await service.consent(session_id, consent_endpoint)
    assert consent is not None


@pytest.mark.asyncio
async def test_consent_declined(fixture: SsoFixture):
    """Service"""

    service: AuthService = await create_service(fixture)
    assert service is not None

    # Kullanıcı sisteme giriş yapar
    login_endpoint: LoginEndpoint = fixture.create_login_endpoint()
    session_id = fixture.generate_new_session_id()

    tenant_id, user_session, auth_request = await service.login(session_id, login_endpoint)
    assert user_session is not None

    # Onay bilgileri oluşturulur. Onay talep edilen izinler verilir
    consent_endpoint: ConsentEndpoint = fixture.create_consent_endpoint(
        accepted=False)
    consent, auth_request = await service.consent(session_id, consent_endpoint)
    assert consent is not None


@pytest.mark.asyncio
async def test_new_password(fixture: SsoFixture):
    """Service"""

    service: AuthService = await create_service(fixture)
    assert service is not None

    register_endpoint: RegisterEndpoint = fixture.create_register_endpoint()
    # Test endpoint yapısındeki email değiştirilerek yeni bir kullanıcı oluşturulur.
    register_endpoint.email = f"{int(random()*1000)}_{register_endpoint.email}"

    tenant_user, user_session, auth_request = await service.register(fixture.session_id, register_endpoint)
    assert tenant_user is not None
    assert user_session is not None
    assert auth_request is not None

    new_password_endpoint: NewPasswordEndpoint = fixture.create_new_password_endpoint(
        register_endpoint.email)
    user = await service.new_password(new_password_endpoint)

    assert user is not None

