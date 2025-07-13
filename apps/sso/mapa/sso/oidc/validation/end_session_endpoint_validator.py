from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from jwt import InvalidTokenError
from mapa.sso.constants import AuthorizeErrors, TokenErrors
from mapa.sso.oidc.end_points.end_session import EndSessionEndpoint
from mapa.sso.oidc.error import InvalidRequestError
from mapa.sso.oidc.token_service import TokenService
from mapa.sso.oidc.validation.end_session_request import EndSessionRequest
from mapa.sso.oidc.validation.validation_result import ValidationResult
from mapa.sso.user_session.user_session_service import UserSessionService


class EndSessionEndPointValidator:
    """End Session servis metoduna gelen isteğine ait parametreleri doğrular.
    Hatalı parametreler olması durumunda hata üretir
    """
    def __init__(
        self,
        user_session_service: UserSessionService,
        token_service: TokenService) -> None:
        self._user_session_service = user_session_service
        self._token_service = token_service

    async def validate(
        self,
        end_session_endpoint: EndSessionEndpoint,
        session_id: UUID
    ) -> ValidationResult[EndSessionRequest]:
        """EndSession servis metoduna gelen parametreleri doğrular"""

        result: Dict[str, Any] = {
            "state": end_session_endpoint.state,
            "post_logout_redirect_uri": end_session_endpoint.post_logout_redirect_uri,
        }

        # Session
        # Eğer session varsa kullanılır aksi halde işleme devam edilir.
        if session_id:
            try:
                result["user_session"] = await self._user_session_service.get(session_id)
            except Exception:
                return ValidationResult(None, error=InvalidRequestError(error_description=AuthorizeErrors.SESSION_NOT_FOUND))

        # Token
        try:
            id_token_payload = await self._token_service.decode_token(end_session_endpoint.id_token_hint)
            if not id_token_payload:
                return ValidationResult(None, error=InvalidRequestError(error_description=TokenErrors.MISSING_TOKEN))
        except InvalidTokenError as exp:
            return ValidationResult(None, error=InvalidRequestError(error_description=TokenErrors.INVALID_TOKEN))
        
        
        result["id_token_payload"] = id_token_payload
        
        # Kullanıcı kontrolü
        if id_token_payload["sub"] != str(result["user_session"].user_id):
            return ValidationResult(None, error=InvalidRequestError(error_description=AuthorizeErrors.INVALID_REQUEST))
        
        return ValidationResult(EndSessionRequest(**result))
