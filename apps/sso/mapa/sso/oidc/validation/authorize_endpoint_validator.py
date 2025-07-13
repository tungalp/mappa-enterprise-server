from uuid import UUID
from mapa.sso.constants import AuthorizeErrors, PromptModes, ResponseModes, ResponseTypes, TokenErrors
from mapa.sso.oidc.end_points.authorize import AuthorizeEndpoint
from mapa.sso.oidc.error import InvalidClientError, InvalidRequestError, InvalidScopeError, UnsupportedResponseModeError, UnsupportedResponseTypeError
from mapa.sso.oidc.validation.authorize_request import AuthorizeRequest
from mapa.sso.oidc.validation.validation_result import ValidationResult
from mapa.sso.user_session.user_session_model import UserSession
from mapa.sso.user_session.user_session_service import UserSessionService
from mapa.sso.constants import GrantTypes
from mapa.sso.messaging.producer.service_messenger import ServiceMessenger

class AuthorizeEndPointValidator:
    """Authorize servis metoduna gelen isteğine ait parametreleri doğrular.
    Hatalı parametreler olması durumunda hata üretir
    """
    grant_types = dict({
        ResponseTypes.CODE: GrantTypes.AUTHORIZATION_CODE,
        ResponseTypes.TOKEN: GrantTypes.IMPLICIT,
        ResponseTypes.IDTOKEN: GrantTypes.IMPLICIT,
        ResponseTypes.IDTOKEN_TOKEN: GrantTypes.IMPLICIT,
        ResponseTypes.CODE_IDTOKEN: GrantTypes.HYBRID,
        ResponseTypes.CODE_TOKEN: GrantTypes.HYBRID,
        ResponseTypes.CODE_IDTOKEN_TOKEN: GrantTypes.HYBRID
    })

    def __init__(
        self,
        user_session_service: UserSessionService,
        messenger: ServiceMessenger) -> None:
        self._user_session_service = user_session_service
        self._messenger = messenger

    async def validate(
        self,
        authorize_endpoint: AuthorizeEndpoint,
        session_id: UUID | None
    ) -> ValidationResult[AuthorizeRequest]:
        """Authorize servis metoduna gelen parametreleri doğrular"""

        result = {
            "state": authorize_endpoint.state,
            "redirect_uri": authorize_endpoint.redirect_uri,
            "max_age": authorize_endpoint.max_age,
            "code_challenge_method": authorize_endpoint.code_challenge_method,
            "code_challenge": authorize_endpoint.code_challenge,
            "nonce": authorize_endpoint.nonce,
            "display": authorize_endpoint.display,
            "ui_locales": authorize_endpoint.ui_locales,
            "id_token_hint": authorize_endpoint.id_token_hint,
            "login_hint": authorize_endpoint.login_hint,
            "acr_values": authorize_endpoint.acr_values,
            "connection": authorize_endpoint.connection,
            "organization": authorize_endpoint.organization,
            "invitation": authorize_endpoint.invitation,
            "screen_hint": authorize_endpoint.screen_hint
        }

        # Session
        # Eğer session varsa kullanılır aksi halde işleme devam edilir.
        if session_id:
            try:
                result["user_session"] = await self._user_session_service.get(session_id)
            except Exception:
                pass

        # Client
        client = await self._messenger.get_client_by_client_id(authorize_endpoint.client_id)
        if not client:
            return ValidationResult(None, error=InvalidClientError())
        result["client"] = client
        
        # Response Type
        response_type = authorize_endpoint.response_type
        if not response_type:
            return ValidationResult(None, error=InvalidRequestError(error_description=AuthorizeErrors.UNSUPPORTED_RESPONSE_TYPE))
        response_types = response_type.split()
        check = all(item in ResponseTypes.to_list() for item in response_types)
        if not check:
            return ValidationResult(None, error=UnsupportedResponseTypeError())
        result["response_types"] = response_types

        # Respose Mode
        if authorize_endpoint.response_mode not in ResponseModes.to_list():
            return ValidationResult(None, error=UnsupportedResponseModeError())
        result["response_mode"] = authorize_endpoint.response_mode

        # Gelen response_type değerlerine göre GrantType belirlenir.
        result["grant_type"] = self.grant_types[response_type]

        # Scope
        scope = authorize_endpoint.scope
        if not scope:
            return ValidationResult(None, error=InvalidScopeError())
        result["scopes"] = scope.split()

        # RedirectUri
        redirect_uri = authorize_endpoint.redirect_uri
        if not redirect_uri or (redirect_uri and client["redirect_uris"] and not redirect_uri in client["redirect_uris"]):
            return ValidationResult(None, error=InvalidRequestError(error_description=AuthorizeErrors.INVALID_REDIRECT_URI))

        # Resources
        audience = authorize_endpoint.audience
        if audience:
            result["audience"] = audience 
 
        # Prompt
        prompt = authorize_endpoint.prompt
        if prompt:
            result["prompt_modes"] = prompt.split()

        # Nonce
        if ResponseTypes.IDTOKEN in result["response_types"] and not authorize_endpoint.nonce:
            return ValidationResult(None, error=InvalidRequestError(error_description=AuthorizeErrors.NONCE_VALUE_REQUIRED))

        return ValidationResult(AuthorizeRequest(**result))
