import jwt
import json
from jwcrypto.jwk import JWK
from datetime import datetime, timedelta
from typing import Any, Dict, List
from uuid import UUID, uuid4
from pydantic import BaseModel
import gzip

from mapa.core.data.base_service import BaseService
from mapa.sso.models import User
from mapa.sso.jwk.jwk_model import JwkModel
from mapa.sso.jwk.jwk_service import JwkService
from mapa.core.data.json_encoder import JsonEncoder


class CreateToken(BaseModel):
    user_id: UUID
    client_id: str
    audience: str
    tenant_id: UUID
    
    
class ClientCredentialsToken(BaseModel):
    client_id: str
    tenant_id: UUID


class TokenService(BaseService):
    """Token üretimi için kullanılan service"""

    def __init__(self, issuer: str, jwk_service: JwkService) -> None:
        self._issuer = issuer
        self._jwk_service = jwk_service
        self._active_jwk_set = None
        super().__init__()

    async def create_access_token(
        self,
        create_token: CreateToken,
        scope: str,
        api_scopes: List[str],
        lifetime: int
    ) -> str:
        """AccessToken"""
        now = datetime.now() - timedelta(seconds=1)
        payload = {
            "iss": self._issuer,
            "sub": str(create_token.user_id),
            "aud": create_token.audience,
            "iat": now.timestamp(),
            "nbf": (now - timedelta(seconds=1)).timestamp(),
            "exp": (now + timedelta(seconds=lifetime)).timestamp(),
            "azp": str(create_token.client_id),
            "jti": str(uuid4()),
            "tenant_id": str(create_token.tenant_id),
            "scope": scope,
            "api_scopes": api_scopes
        }

        jwk_list = await self._jwk_service.get_active_set()
        private_key = jwk_list[0].private_pem
        kid = jwk_list[0].key_id
        jwt_token = jwt.encode(payload, private_key, algorithm='RS256', headers={
            "kid": kid
        })
        return jwt_token
    
    async def create_access_token_client_credentials(
        self,
        create_token: ClientCredentialsToken,
        scope: str,
        api_scopes: List[str],
        lifetime: int
    ) -> str:
        """AccessToken"""
        now = datetime.now() - timedelta(seconds=1)
        payload = {
            "iss": self._issuer,
            "sub": str(create_token.client_id),
            "iat": now.timestamp(),
            "nbf": (now - timedelta(seconds=1)).timestamp(),
            "exp": (now + timedelta(seconds=lifetime)).timestamp(),
            "azp": str(create_token.client_id),
            "jti": str(uuid4()),
            "tenant_id": str(create_token.tenant_id),
            "scope": scope,
            "api_scopes": api_scopes
        }

        jwk_list = await self._jwk_service.get_active_set()
        private_key = jwk_list[0].private_pem
        kid = jwk_list[0].key_id
        jwt_token = jwt.encode(payload, private_key, algorithm='RS256', headers={
            "kid": kid
        })
        return jwt_token
       

    async def create_id_token(
        self,
        create_token: CreateToken,
        user: User,
        lifetime: int,
        nonce: str
    ) -> str:
        """IdToken"""

        now = datetime.now() - timedelta(seconds=1)
        payload = {
            "iss": self._issuer,
            "sub": str(create_token.user_id),
            "aud": create_token.client_id,
            "iat": now.timestamp(),
            "nbf": (now - timedelta(seconds=1)).timestamp(),
            "exp": (now + timedelta(seconds=lifetime)).timestamp(),
            "name": f"{user.name} {user.surname}",
            "given_name": user.name,
            "family_name": user.surname,
            "email": user.email,
            "email_verified": user.email_verified,
            "picture": "",
            "nonce": nonce
        }
        jwk_list = await self._jwk_service.get_active_set()
        private_key = jwk_list[0].private_pem
        kid = jwk_list[0].key_id        
        jwt_token = jwt.encode(payload, private_key, algorithm='RS256', headers={
            "kid": kid
        })
        return jwt_token

    async def decode_token(self, token: str) -> Dict[str, Any]:
        options = {
            "verify_aud": False,
            "verify_iat": False
        }
        unverified_header = jwt.get_unverified_header(token)
        kid = str(unverified_header.get("kid"))
        jwk_model = await self.get_jwk_with_kid(kid)
        if not jwk_model:
            raise ValueError(f"JWT not found. kid = {kid}")
        public_key = jwk_model.public_pem
        return jwt.decode(
            token, public_key, algorithms=["RS256"], options=options, issuer=self._issuer)

    async def get_active_jwk_set(self) -> List[JwkModel]:
        if not self._active_jwk_set or self._active_jwk_set[0].expired_at < datetime.now():
            self._active_jwk_set = await self._jwk_service.get_active_set()
        return self._active_jwk_set

    async def get_jwk_with_kid(self, kid: str) -> JwkModel | None:
        jwk_list = await self.get_active_jwk_set()
        return next(filter(lambda x: x.key_id == kid, jwk_list), None)