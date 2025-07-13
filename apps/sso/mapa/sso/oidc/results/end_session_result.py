import json
from string import Template
from typing import Any, Dict, Union
from mapa.sso.auth.consent_endpoint import ConsentEndpoint
from mapa.sso.auth.login_endpoint import LoginEndpoint
from mapa.sso.constants import ResponseModes
from mapa.sso.oidc.end_points.authorize import AuthorizeEndpoint
from urllib.parse import urlencode, urlparse
from mapa.sso.oidc.end_points.end_session import EndSessionEndpoint
from mapa.sso.oidc.response_handling.authorize_error_response import AuthorizeErrorResponse
from mapa.sso.oidc.response_handling.authorize_response import AuthorizeResponse
from mapa.sso.oidc.response_handling.end_session_response import EndSessionResponse
from mapa.sso.oidc.response_handling.interaction_response import InteractionResponse


class EndSessionResult:
    """EndSession metodunun dönüş nesnesi"""

    def  execute(
        self, response: EndSessionResponse) -> Any:
        """Response nesnesinden dönüş değeri oluşturur."""

        uri = response.redirect_uri
        state = response.state
        uri += ("?state=" + state if state else "")

        return {
            "type": "redirect",
            "url": uri
        }

    def execute_error(self, endpoint: EndSessionEndpoint, error: AuthorizeErrorResponse) -> Any:
        """Hata bilgisi url olarak oluşturulur."""

        uri = endpoint.post_logout_redirect_uri
        error_dict = self.__to_dict(error)
        return uri + ("?" + urlencode(error_dict))

    def __to_dict(self, obj: Any) -> Dict[str, Any]:
        return dict(filter(lambda item: item[1] is not None, vars(obj).items()))
