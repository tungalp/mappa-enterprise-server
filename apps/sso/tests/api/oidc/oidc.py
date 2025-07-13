from mapa.manage.organization.organization_service import OrganizationService
from mapa.manage.organization_client.organization_client_service import OrganizationClientService
from mapa.sso.auth.auth_util_service import AuthUtilService
from mapa.sso.auth.interaction_service import InteractionService
from mapa.sso.authorization_code.authorization_code_service import AuthorizatioCodeService
from mapa.manage.client.client_service import ClientService
from mapa.sso.consent.consent_service import ConsentService
from mapa.sso.jwk.jwk_service import JwkService
from mapa.sso.oidc.oidc_service import OidcService
from mapa.sso.oidc.response_handling.authorize_response_handler import AuthorizeResponseHandler
from mapa.sso.oidc.response_handling.end_session_response_handler import EndSessionResponseHandler
from mapa.sso.oidc.response_handling.interaction_response_handler import InteractionResponseHandler
from mapa.sso.oidc.response_handling.revocation_response_handler import RevocationResponseHandler
from mapa.sso.oidc.response_handling.token_response_handler import TokenResponseHandler
from mapa.sso.oidc.token_service import TokenService
from mapa.sso.oidc.validation.authorize_endpoint_validator import AuthorizeEndPointValidator
from mapa.sso.oidc.validation.end_session_endpoint_validator import EndSessionEndPointValidator
from mapa.sso.oidc.validation.revocation_endpoint_validator import RevocationEndPointValidator
from mapa.sso.oidc.validation.token_endpoint_validator import TokenEndPointValidator
from mapa.sso.refresh_token.refresh_token_service import RefreshTokenService
from mapa.manage.tenant_client.tenant_client_service import TenantClientService
from mapa.manage.tenant_user.tenant_user_service import TenantUserService
from mapa.manage.user.user_service import UserService
from mapa.sso.user_session.user_session_service import UserSessionService
from mapa.sso.user_session_client.user_session_client_service import UserSessionClientService
from mapa.manage.api.api_service import ApiService
from ..conftest import SsoFixture

from ..conftest import SsoFixture

async def create_service(fixture: SsoFixture) -> OidcService:
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True

    async_db = fixture.create_db_instance(fixture.db_url_async)
    tenant_client_service = TenantClientService(async_db)
    client_service = ClientService(async_db, tenant_client_service)
    auth_code_service = AuthorizatioCodeService(async_db)
    consent_service = ConsentService(async_db)
    user_session_service = UserSessionService(async_db)
    user_session_client_service = UserSessionClientService(async_db)
    interaction_service = InteractionService(consent_service)
    tenant_user_service = TenantUserService(async_db)

    authorize_validator = AuthorizeEndPointValidator(
        client_service, user_session_service)
    authorize_handler = AuthorizeResponseHandler(
        auth_code_service,
        user_session_client_service,
        tenant_user_service)
    interaction_handler = InteractionResponseHandler(interaction_service)

    jwt_secret = "b3AXVPcKEL8UPZ07TgPYA"
    util_service = AuthUtilService(jwt_secret)

    jwk_service = JwkService(async_db)

    token_service = TokenService(
        issuer="https://sso.mapa.com.tr",
        jwk_service=jwk_service
    )

    refresh_token_service = RefreshTokenService(async_db)

    tenant_client_service = TenantClientService(async_db)
    token_validator = TokenEndPointValidator(
        client_service,
        auth_code_service,
        user_session_service,
        refresh_token_service,
        tenant_client_service,
        user_session_client_service,
        util_service)

    api_service = ApiService(async_db)
    organization_client_service = OrganizationClientService(async_db)
    organization_service = OrganizationService(async_db, organization_client_service)
    user_service = UserService(async_db, api_service, organization_service)
    short_token_lifetime = 7200
    long_token_lifetime = 86400
    id_token_lifetime = 36000
    refresh_token_lifetime = 2592000

    token_handler = TokenResponseHandler(
        token_service=token_service,
        user_service=user_service,
        refresh_token_service=refresh_token_service,
        short_token_lifetime=short_token_lifetime,
        long_token_lifetime=long_token_lifetime,
        id_token_lifetime=id_token_lifetime,
        refresh_token_lifetime=refresh_token_lifetime
    )

    end_session_validator = EndSessionEndPointValidator(
        user_session_service=user_session_service,
        token_service=token_service
    )
    end_session_handler = EndSessionResponseHandler(
        user_session_service=user_session_service
    )
    
    revocation_validator = RevocationEndPointValidator(
        client_service=client_service,
        refresh_token_service=refresh_token_service
    )
    revocation_handler = RevocationResponseHandler(
        refresh_token_service=refresh_token_service
    )    

    return OidcService(
        fixture.app_host,
        authorize_validator,
        authorize_handler,
        interaction_handler,
        token_validator,
        token_handler,
        end_session_validator,
        end_session_handler,
        revocation_validator,
        revocation_handler
    )
