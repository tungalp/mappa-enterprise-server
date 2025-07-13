from typing import Any, Optional, Tuple
from jwt import DecodeError, PyJWKClientError, decode, PyJWKClient
from starlette.authentication import (
    AuthenticationBackend,
    AuthCredentials,
    BaseUser,
    AuthenticationError,
    UnauthenticatedUser
)
from starlette.requests import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


class AuthenticatedUser(BaseUser):
    """Yetkili kullanıcının token bilgisini tutar.
    """
    def __init__(self, sub: str, payload: Any) -> None:
        self.sub = sub
        self.payload = payload
        
    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        try:
            return self.payload["display_name"]
        except Exception:
            return self.sub

    @property
    def identity(self) -> str:
        return self.sub
    
    @property
    def tenant_id(self) -> str:
        try:
            return self.payload["tenant_id"]
        except Exception as ex:
            raise ValueError("TenantId not found") from ex


token_auth_scheme = HTTPBearer()


class OAuth2IdTokenBackend(AuthenticationBackend):
    """
    Handle authentication via OAuth2 id-token (implicit flow, authorization code, with or without PKCE)
    """

    def __init__(self, jwks_uri: str):
        """jwks_uri: The JWKs URI as defined in .well-known."""
        self.signing_key = ""
        self.jwks_client = PyJWKClient(jwks_uri)
        
    @property
    def jwks_uri(self) -> str:
        return self.jwks_client.uri
    
    @jwks_uri.setter
    def jwks_uri(self, value: str):
        self.jwks_client = PyJWKClient(value)

    async def authenticate(
        self, conn: Request
    ) -> Optional[Tuple["AuthCredentials", "BaseUser"]]:
        try:
            # Header dan token alınır. Eğer token tanımlı değilse yetkili olmayan kullanıcı oluşturulur.
            token: HTTPAuthorizationCredentials = await token_auth_scheme(conn)  # type: ignore
        except Exception:
            return (
                AuthCredentials(),
                UnauthenticatedUser()
            )
        
        try:
            # This gets the 'kid' from the passed token            
            self.signing_key = self.jwks_client.get_signing_key_from_jwt(
                token.credentials
            ).key
        except PyJWKClientError as ex:
            raise AuthenticationError(str(ex)) from ex
        except DecodeError as ex:
            raise AuthenticationError(str(ex)) from ex

        try:
            payload = decode(
                token.credentials,
                self.signing_key,
                algorithms=["RS256"],
                options={"verify_aud": False}
            )
            scopes = []
            if payload["scope"]:
                scopes.extend(payload["scope"].split(' '))
            if payload["api_scopes"]:
                scopes.extend(payload["api_scopes"])
            return (
                AuthCredentials(scopes=[*set(scopes)]),
                AuthenticatedUser(payload["sub"], payload)
            )
        except Exception as ex:
            raise AuthenticationError(str(ex)) from ex
