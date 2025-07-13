from datetime import datetime
from mapa.sso.oidc.response_handling.authorize_error_response import AuthorizeErrorResponse
from mapa.sso.oidc.response_handling.end_session_response import EndSessionResponse
from mapa.sso.oidc.validation.end_session_request import EndSessionRequest
from mapa.sso.user_session.user_session_model import UpdateUserSession
from mapa.sso.user_session.user_session_service import UserSessionService


class EndSessionResponseHandler:
    """Doğrulanmış EndSession isteğini işleyerek uygun dönüş 
    değerini oluşturur.
    """

    def __init__(
        self,
        user_session_service: UserSessionService
    ) -> None:
        self._user_session_service = user_session_service

    async def create_response(self, end_session_request: EndSessionRequest) -> EndSessionResponse | AuthorizeErrorResponse:
        """EndSession servisine gelen isteği işler. """

        if end_session_request.user_session.authenticated:
            await self._user_session_service.update(end_session_request.user_session.id, UpdateUserSession(
                authenticated=False,
                authenticated_at=datetime.now()
            ))
        
        return EndSessionResponse(
            redirect_uri=end_session_request.post_logout_redirect_uri,
            state=end_session_request.state
        )
