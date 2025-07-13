from mapa.sso.constants import TokenErrors
from mapa.sso.oidc.response_handling.authorize_error_response import AuthorizeErrorResponse
from mapa.sso.oidc.validation.revocation_request import RevocationRequest
from mapa.sso.refresh_token.refresh_token_model import UpdateRefreshToken
from mapa.sso.refresh_token.refresh_token_service import RefreshTokenService

class RevocationResponseHandler:
    """Doğrulanmış revocation isteğini işleyerek uygun dönüş 
    değerini oluşturur.
    """

    def __init__(
        self,
        refresh_token_service: RefreshTokenService,
    ) -> None:
        self._refresh_token_service = refresh_token_service

    async def create_response(self, revocation_request: RevocationRequest) -> AuthorizeErrorResponse | None:
        """Revocation servisine gelen isteği işler. Gelen isteğin durumuna göre akışları tanımlar"""
        
        refresh_token_id = revocation_request.refresh_token.id
        updated = await self._refresh_token_service.update(refresh_token_id, UpdateRefreshToken(
            is_active=False
        ))
        if updated.is_active:
            return AuthorizeErrorResponse(
                error=TokenErrors.INVALID_REQUEST,
                error_description=TokenErrors.INVALID_REQUEST
            )
