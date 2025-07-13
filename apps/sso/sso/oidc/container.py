from dependency_injector import containers
from dependency_injector import providers
from mapa.sso.auth.interaction_service import InteractionService
from mapa.sso.authorization_code.authorization_code_service import (
    AuthorizatioCodeService,
)
from mapa.sso.jwk.jwk_service import JwkService

from mapa.sso.oidc.oidc_service import OidcService
from mapa.sso.oidc.response_handling.authorize_response_handler import (
    AuthorizeResponseHandler,
)
from mapa.sso.oidc.response_handling.end_session_response_handler import (
    EndSessionResponseHandler,
)
from mapa.sso.oidc.response_handling.interaction_response_handler import (
    InteractionResponseHandler,
)
from mapa.sso.oidc.response_handling.revocation_response_handler import (
    RevocationResponseHandler,
)
from mapa.sso.oidc.response_handling.token_response_handler import TokenResponseHandler
from mapa.sso.oidc.token_service import TokenService
from mapa.sso.oidc.validation.authorize_endpoint_validator import (
    AuthorizeEndPointValidator,
)
from mapa.sso.oidc.validation.end_session_endpoint_validator import (
    EndSessionEndPointValidator,
)
from mapa.sso.oidc.validation.revocation_endpoint_validator import (
    RevocationEndPointValidator,
)
from mapa.sso.oidc.validation.token_endpoint_validator import TokenEndPointValidator
from mapa.sso.refresh_token.refresh_token_service import RefreshTokenService


class OidcContainer(containers.DeclarativeContainer):
    """Kimliklendirme paketinin bağımlılık konteyneri"""

    # OIDC ile ilgili konfigürasyon parametreleri
    config = providers.Configuration()

    # Servis Bağımlılıkları
    database = providers.Dependency()
    consent_service = providers.Dependency()
    user_session_service = providers.Dependency()
    user_session_client_service = providers.Dependency()
    util_service = providers.Dependency()
    messenger = providers.Dependency()

    # Bu pakete bağlı servisler
    authorization_code_service = providers.Factory(
        AuthorizatioCodeService, async_db=database
    )

    interaction_service = providers.Factory(
        InteractionService, consent_service=consent_service
    )

    jwk_service = providers.Factory(JwkService, async_db=database)

    token_service = providers.Factory(
        TokenService, issuer=config.oidc.issuer, jwk_service=jwk_service
    )

    refresh_token_service = providers.Factory(RefreshTokenService, async_db=database)

    # Validators
    authorize_validator = providers.Factory(
        AuthorizeEndPointValidator,
        user_session_service=user_session_service,
        messenger = messenger
    )

    token_validator = providers.Factory(
        TokenEndPointValidator,
        authorization_code_service=authorization_code_service,
        user_session_service=user_session_service,
        refresh_token_service=refresh_token_service,
        user_session_client_service=user_session_client_service,
        util_service=util_service,
        messenger = messenger
    )

    end_session_validator = providers.Factory(
        EndSessionEndPointValidator,
        user_session_service=user_session_service,
        token_service=token_service,
    )

    revocation_validator = providers.Factory(
        RevocationEndPointValidator,
        refresh_token_service=refresh_token_service,
        messenger = messenger
    )

    # Handlers
    authorize_handler = providers.Factory(
        AuthorizeResponseHandler,
        authorization_code_service=authorization_code_service,
        user_session_client_service=user_session_client_service,
        messenger = messenger
    )

    token_handler = providers.Factory(
        TokenResponseHandler,
        token_service=token_service,
        refresh_token_service=refresh_token_service,
        short_token_lifetime=config.oidc.short_token_lifetime,
        long_token_lifetime=config.oidc.long_token_lifetime,
        id_token_lifetime=config.oidc.id_token_lifetime,
        refresh_token_lifetime=config.oidc.refresh_token_lifetime,
        messenger = messenger
    )

    interaction_handler = providers.Factory(
        InteractionResponseHandler, interaction_service=interaction_service
    )

    end_session_handler = providers.Factory(
        EndSessionResponseHandler, user_session_service=user_session_service
    )

    revocation_handler = providers.Factory(
        RevocationResponseHandler, refresh_token_service=refresh_token_service
    )

    # Servis
    oidc_service = providers.Factory(
        OidcService,
        app_host=config.oidc.app_host,
        authorize_validator=authorize_validator,
        authorize_handler=authorize_handler,
        interaction_handler=interaction_handler,
        token_validator=token_validator,
        token_handler=token_handler,
        end_session_validator=end_session_validator,
        end_session_handler=end_session_handler,
        revocation_validator=revocation_validator,
        revocation_handler=revocation_handler,
    )
