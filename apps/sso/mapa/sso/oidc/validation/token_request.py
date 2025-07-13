from uuid import UUID
from pydantic import BaseModel
from mapa.sso.models import Client
from mapa.sso.authorization_code.authorization_code_model import AuthorizationCode
from mapa.sso.refresh_token.refresh_token_model import RefreshToken
from mapa.sso.user_session.user_session_model import UserSession


class TokenRequest(BaseModel):
    """Doğrulanmış Token isteği"""

    client: Client
    grant_type: str
    tenant_id: UUID
    language: str | None = None


class AuthorizationCodeTokenRequest(TokenRequest):
    redirect_uri: str
    code: AuthorizationCode
    audience: str
    code_verifier: str | None = None
    user_session: UserSession


class ClientCredentialsTokenRequest(TokenRequest):
    access_token: str | None = None


class RefreshTokenTokenRequest(TokenRequest):
    refresh_token: RefreshToken
    user_session: UserSession
