import base64
from datetime import datetime, timedelta
import hashlib
import secrets
import string
from typing import Any, Dict, List
from urllib import parse

import jwt
from mapa.core.data.base_service import BaseService
from mapa.sso.auth.forgot_password_endpoint import ForgotPasswordEndpoint
from mapa.sso.constants import CodeChallengeMethods, PromptModes, ResponseTypes, StandardScopes


class AuthUtilService(BaseService):

    def __init__(self,
                 jwt_secret: str) -> None:
        self._jwt_secret = jwt_secret
        super().__init__()


    def create_new_password_link(self, app_host: str, forgot_password_endpoint: ForgotPasswordEndpoint) -> Dict:
        # app_host = self._app_host
        data = {
            "email": forgot_password_endpoint.email,
            "expired_at": (datetime.now() + timedelta(minutes=10080)).timestamp()
        }
        token = jwt.encode(data, self._jwt_secret, "HS256")

        req = {
            "audience": forgot_password_endpoint.audience,
            "client_id": forgot_password_endpoint.client_id,
            "response_type": ResponseTypes.CODE,
            "nonce": self.generate_secret(64),
            "state": self.generate_secret(128),
            "code_challenge": self.generate_code_challenge(self.generate_code_verifier()),
            "code_challenge_method": CodeChallengeMethods.SHA256,
            "redirect_uri": forgot_password_endpoint.redirect_uri,
            "token": token,
            "scope": forgot_password_endpoint.scope,
            "language": forgot_password_endpoint.lang
        }

        url = f"{app_host}/new-password?{parse.urlencode(req)}"
        return {
            "type": "redirect",
            "url": url
        }

    # def create_register_link(self, app_host: str, audience: str, client_id: str, redirect_uri: str, email: str, language: str) -> Dict:
    #     req = {
    #         "email": email,
    #         "client_id": client_id,
    #         "scope": f"{StandardScopes.OPENID} {StandardScopes.PROFILE} {StandardScopes.EMAIL}",
    #         "audience": audience,
    #         "response_type": ResponseTypes.CODE,
    #         "nonce": self.generate_secret(64),
    #         "state": self.generate_secret(128),
    #         "code_challenge": self.generate_code_challenge(self.generate_code_verifier()),
    #         "code_challenge_method": CodeChallengeMethods.SHA256,
    #         "redirect_uri": redirect_uri,
    #         "screen_hint": f"{PromptModes.REGISTER}",
    #         "language": language
    #     }
    #     url = f"{app_host}/register?{parse.urlencode(req)}"
    #     return {
    #         "type": "redirect",
    #         "url": url
    #     }

    def generate_secret(self, size: int = 32) -> str:
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for i in range(size))

    def generate_code_verifier(self, length: int = 64) -> str:
        """Random PKCE-compliant code verifier.
        """
        if not 43 <= length <= 128:
            msg = 'Parameter `length` must verify `43 <= length <= 128`.'
            raise ValueError(msg)
        code_verifier = secrets.token_urlsafe(96)[:length]
        return code_verifier

    def generate_code_challenge(self, code_verifier: str) -> str:
        """PKCE-compliant code challenge for a given verifier
        """
        if not 43 <= len(code_verifier) <= 128:
            msg = 'Parameter `code_verifier` must verify '
            msg += '`43 <= len(code_verifier) <= 128`.'
            raise ValueError(msg)
        hashed = hashlib.sha256(code_verifier.encode('ascii')).digest()
        encoded = base64.urlsafe_b64encode(hashed)
        code_challenge = encoded.decode('ascii')[:-1]
        return code_challenge
