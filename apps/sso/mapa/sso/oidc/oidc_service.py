"""OpenID Service
"""
from typing import Tuple
from uuid import UUID
from mapa.sso.constants import AuthorizeErrors
from mapa.sso.oidc.end_points.authorize import AuthorizeEndpoint
from mapa.sso.oidc.end_points.end_session import EndSessionEndpoint
from mapa.sso.oidc.end_points.revocation import RevocationEndpoint
from mapa.sso.oidc.end_points.token import TokenEndpoint
from mapa.sso.oidc.response_handling.authorize_error_response import AuthorizeErrorResponse
from mapa.sso.oidc.response_handling.authorize_response import AuthorizeResponse
from mapa.sso.oidc.response_handling.authorize_response_handler import AuthorizeResponseHandler
from mapa.sso.oidc.response_handling.end_session_response import EndSessionResponse
from mapa.sso.oidc.response_handling.end_session_response_handler import EndSessionResponseHandler
from mapa.sso.oidc.response_handling.interaction_response import InteractionResponse
from mapa.sso.oidc.response_handling.interaction_response_handler import InteractionResponseHandler
from mapa.sso.oidc.response_handling.revocation_response_handler import RevocationResponseHandler
from mapa.sso.oidc.response_handling.token_response import TokenResponse
from mapa.sso.oidc.response_handling.token_response_handler import TokenResponseHandler
from mapa.sso.oidc.validation.authorize_endpoint_validator import AuthorizeEndPointValidator
from mapa.sso.oidc.validation.end_session_endpoint_validator import EndSessionEndPointValidator
from mapa.sso.oidc.validation.revocation_endpoint_validator import RevocationEndPointValidator
from mapa.sso.oidc.validation.token_endpoint_validator import TokenEndPointValidator

class OidcService:
    """OpenID Service
    """

    def __init__(
        self,
        app_host: str,
        authorize_validator: AuthorizeEndPointValidator,
        authorize_handler: AuthorizeResponseHandler,
        interaction_handler: InteractionResponseHandler,
        token_validator: TokenEndPointValidator,
        token_handler: TokenResponseHandler,
        end_session_validator: EndSessionEndPointValidator,
        end_session_handler: EndSessionResponseHandler,
        revocation_validator: RevocationEndPointValidator,
        revocation_handler: RevocationResponseHandler

    ) -> None:
        self._app_host = app_host
        # Authorize
        self._authorize_validator = authorize_validator
        self._authorize_handler = authorize_handler
        self._interaction_handler = interaction_handler

        # Token
        self._token_validator = token_validator
        self._token_handler = token_handler
        
        # End Session
        self._end_session_validator = end_session_validator
        self._end_session_handler = end_session_handler

        # Revoke Token
        self._revocation_validator = revocation_validator
        self._revocation_handler = revocation_handler

    async def authorize(self,
                        authorize_endpoint: AuthorizeEndpoint,
                        session_id: UUID | None
                        ) -> Tuple[AuthorizeResponse | InteractionResponse | None, AuthorizeErrorResponse | None]:
        """/authorize servis metodununa gelen isteğin işlendiği metotdur."""

        # Gelen isteğin parametreleri doğrulanır.
        val_result = await self._authorize_validator.validate(authorize_endpoint, session_id)
        if val_result.error:
            # Hata dönüşü yapılacak
            return (None, AuthorizeErrorResponse(
                error=val_result.error.error,
                error_description=val_result.error.error_description
            ))
        if val_result.result:
            # Kullanıcı etkileşimine ihtiyaç olup olmadığı kontrol edilir.
            response = await self._interaction_handler.create_response(val_result.result)
            # Eğer etkileşim bulunamadıysa authorization işlemi yapılır
            if not response:
                response = await self._authorize_handler.create_response(val_result.result)

            return (response if not isinstance(response, AuthorizeErrorResponse) else None,
                    response if isinstance(response, AuthorizeErrorResponse) else None)
        else:
            return (None, AuthorizeErrorResponse(error=AuthorizeErrors.SERVER_ERROR))

    async def token(
        self, token_endpoint: TokenEndpoint
    ) -> Tuple[TokenResponse | None, AuthorizeErrorResponse | None]:
        """/token servis metodununa gelen isteğin işlendiği metotdur."""
        val_result = await self._token_validator.validate(token_endpoint)
        if val_result.error:
            # Hata dönüşü yapılacak
            return (None, AuthorizeErrorResponse(
                error=val_result.error.error,
                error_description=val_result.error.error_description
            ))
        if val_result.result:
            # Kullanıcı etkileşimine ihtiyaç olup olmadığı kontrol edilir.
            response = await self._token_handler.create_response(val_result.result)

            return (response if not isinstance(response, AuthorizeErrorResponse) else None,
                    response if isinstance(response, AuthorizeErrorResponse) else None)
        else:
            return (None, AuthorizeErrorResponse(error=AuthorizeErrors.SERVER_ERROR))

    async def end_session(self, end_session_endpoint: EndSessionEndpoint, session_id: UUID) -> EndSessionResponse | AuthorizeErrorResponse:
        """/endsession servis metodununa gelen isteğin işlendiği metotdur."""

        val_result = await self._end_session_validator.validate(end_session_endpoint, session_id)
        if val_result.error:
            # Hata dönüşü yapılacak
            return AuthorizeErrorResponse(
                error=val_result.error.error,
                error_description=val_result.error.error_description
            )

        return await self._end_session_handler.create_response(val_result.result)  # type: ignore

    async def revoke_token(self, revocation_endpoint: RevocationEndpoint) -> AuthorizeErrorResponse | None:
        """/revocation servis metodununa gelen isteğin işlendiği metotdur."""

        val_result = await self._revocation_validator.validate(revocation_endpoint)
        if val_result.error:
            # Hata dönüşü yapılacak
            return AuthorizeErrorResponse(
                error=val_result.error.error,
                error_description=val_result.error.error_description
            )

        return await self._revocation_handler.create_response(val_result.result)  # type: ignore