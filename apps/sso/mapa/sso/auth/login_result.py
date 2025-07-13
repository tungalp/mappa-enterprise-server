from urllib import parse
from mapa.sso.auth.login_endpoint import LoginEndpoint
from mapa.sso.user_session.user_session_model import UserSession


class LoginResult:
    """Login işleminin dönüş değeri"""

    def __init__(self, api_host: str, login_endpoint: LoginEndpoint, user_session: UserSession) -> None:
        self._api_host = api_host
        self._login_endpoint = login_endpoint
        self._user_session = user_session

    def execute(self):
        req_dict = {k: v for k, v in vars(
            self._login_endpoint).items() if v is not None}
        del req_dict["email"]
        del req_dict["password"]

        # Eğer giriş yaptıysa authorize işlemine devam edilir.
        if not self._user_session.authenticated:
            return {
                "type": "json",
                "status_code": 401,
                "detail": "User authenticaion failed"
            }

        url = f"{self._api_host}/api/sso/oidc/authorize?{parse.urlencode(req_dict)}"            
        return {
            "type": "redirect",
            "url": url
        }
