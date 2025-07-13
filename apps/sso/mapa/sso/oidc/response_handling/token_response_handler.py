from datetime import datetime, timedelta
from typing import List
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.sso.constants import TokenErrors
from mapa.sso.messaging.producer.service_messenger import ServiceMessenger
from mapa.sso.models import User
from mapa.sso.oidc.response_handling.authorize_error_response import (
    AuthorizeErrorResponse,
)
from mapa.sso.oidc.response_handling.token_response import TokenResponse
from mapa.sso.oidc.token_service import ClientCredentialsToken, CreateToken, TokenService
from mapa.sso.oidc.validation.token_request import (
    AuthorizationCodeTokenRequest,
    ClientCredentialsTokenRequest,
    RefreshTokenTokenRequest,
    TokenRequest,
)
from mapa.sso.refresh_token.refresh_token_model import (
    CreateRefreshToken,
    UpdateRefreshToken,
)
from mapa.sso.refresh_token.refresh_token_service import RefreshTokenService
from mapa.sso.constants import GrantTypes


class TokenResponseHandler:
    """Doğrulanmış token isteğini işleyerek uygun dönüş
    değerini oluşturur.
    """

    def __init__(
        self,
        token_service: TokenService,
        refresh_token_service: RefreshTokenService,
        short_token_lifetime: int,
        long_token_lifetime: int,
        id_token_lifetime: int,
        refresh_token_lifetime: int,
        messenger: ServiceMessenger
    ) -> None:
        self._token_service = token_service
        self._refresh_token_service = refresh_token_service
        self._short_token_lifetime = short_token_lifetime
        self._long_token_lifetime = long_token_lifetime
        self._id_token_lifetime = id_token_lifetime
        self._refresh_token_lifetime = refresh_token_lifetime
        self._messenger = messenger

    async def create_response(
        self, token_request: TokenRequest
    ) -> TokenResponse | AuthorizeErrorResponse:
        """Authorize servisine gelen isteği işler. Gelen isteğin durumuna göre akışları tanımlar"""
        if token_request.grant_type == GrantTypes.AUTHORIZATION_CODE:
            return await self.create_auth_code_response(token_request)
        elif token_request.grant_type == GrantTypes.REFRESH_TOKEN:
            return await self.create_refresh_token_response(token_request)
        elif token_request.grant_type == GrantTypes.IMPLICIT:
            return await self.create_implicit_response(token_request)
        elif token_request.grant_type == GrantTypes.HYBRID:
            return await self.create_hybrid_response(token_request)
        elif token_request.grant_type == GrantTypes.CLIENT_CREDENTIALS:
            return await self.create_client_credentials(token_request)
        else:
            return AuthorizeErrorResponse(
                error=TokenErrors.INVALID_GRANT,
                error_description=",".join(
                    [res_type for res_type in token_request.grant_type]
                ),
            )

    async def create_auth_code_response(
        self, token_request: TokenRequest
    ) -> TokenResponse:
        """AuthorizeResponse oluşturur."""
        auth_code_request: AuthorizationCodeTokenRequest = token_request  # type: ignore
        user = await self._messenger.get_by_user_id(str(auth_code_request.code.user_id))
        api_scopes: List[str] = await self._messenger.get_user_scopes(
            str(auth_code_request.client.id),
            str(user["id"]),
            str(auth_code_request.tenant_id),
        )
        standart_scope = "openid profile email"
        create_token = CreateToken(
            user_id=user["id"],
            audience=auth_code_request.audience,
            client_id=auth_code_request.client.client_id,
            tenant_id=auth_code_request.tenant_id,
        )
        access_token = await self._token_service.create_access_token(
            create_token, standart_scope, api_scopes, self._short_token_lifetime
        )
        id_token = await self._token_service.create_id_token(
            create_token, User(**user), self._id_token_lifetime, auth_code_request.code.nonce
        )
        refresh_token = None
        now = datetime.now()
        if "offline_access" in auth_code_request.code.scopes:
            standart_scope += " offline_access"
            refresh_token = await self._refresh_token_service.find_one(
                QueryArgs(
                    where=[
                        Filter(
                            field="user_session_id",
                            op=FilterOp.EQUAL,
                            value=auth_code_request.code.user_session_id,
                        ),
                        Filter(
                            field="user_id",
                            op=FilterOp.EQUAL,
                            value=auth_code_request.code.user_id,
                        ),
                        Filter(
                            field="client_id",
                            op=FilterOp.EQUAL,
                            value=auth_code_request.code.client_id,
                        ),
                        Filter(
                            field="nonce",
                            op=FilterOp.EQUAL,
                            value=auth_code_request.code.nonce,
                        ),
                        Filter(field="is_active", op=FilterOp.EQUAL, value=True),
                        Filter(field="expired_at", op=FilterOp.MORE_THAN, value=now),
                    ]
                )
            )
            if not refresh_token:
                refresh_token = await self._refresh_token_service.create(
                    CreateRefreshToken(
                        user_session_id=auth_code_request.code.user_session_id,
                        user_id=auth_code_request.code.user_id,
                        client_id=auth_code_request.code.client_id,
                        audience=auth_code_request.audience,
                        created_at=now,
                        expired_at=now
                        + timedelta(seconds=self._refresh_token_lifetime),
                        nonce=auth_code_request.code.nonce,
                    )
                )

        return TokenResponse(
            token_type="Bearer",
            expires_in=self._short_token_lifetime,
            access_token=access_token,
            id_token=id_token,
            refresh_token=str(refresh_token.id) if refresh_token else None,
            tenant_id=str(auth_code_request.tenant_id),
            scope=standart_scope,
            api_scopes=api_scopes,
            nonce=auth_code_request.code.nonce,
            language=token_request.language,
        )

    async def create_refresh_token_response(
        self, token_request: TokenRequest
    ) -> TokenResponse:
        """AuthorizeResponse oluşturur."""

        refresh_token_request: RefreshTokenTokenRequest = token_request  # type: ignore
        user = await self._messenger.get_by_user_id(str(refresh_token_request.refresh_token.user_id))
        api_scopes: List[str] = await self._messenger.get_user_scopes(
            str(refresh_token_request.client.id),
            str(user["id"]),
            str(refresh_token_request.tenant_id),
        )
        standart_scope = "openid profile email"
        create_token = CreateToken(
            user_id=user["id"],
            audience=refresh_token_request.refresh_token.audience,
            client_id=refresh_token_request.client.client_id,
            tenant_id=refresh_token_request.tenant_id,
        )
        access_token = await self._token_service.create_access_token(
            create_token, standart_scope, api_scopes, self._short_token_lifetime
        )
        id_token = await self._token_service.create_id_token(
            create_token,
            User(**user),
            self._id_token_lifetime,
            refresh_token_request.refresh_token.nonce,
        )  # type: ignore
        # Refresh Token
        refresh_token = refresh_token_request.refresh_token
        now = datetime.now()
        # Refresh token süresi bitecekse yeni bir refresh token üretilir aksi durumda varolan kullanılır.
        if (
            refresh_token.expired_at - timedelta(seconds=self._short_token_lifetime * 2)
            < datetime.now()
        ):
            refresh_token = await self._refresh_token_service.create(
                CreateRefreshToken(
                    user_session_id=refresh_token_request.user_session.id,
                    user_id=refresh_token_request.refresh_token.user_id,
                    client_id=refresh_token_request.client.client_id,
                    audience=refresh_token_request.refresh_token.audience,
                    created_at=now,
                    expired_at=now + timedelta(seconds=self._refresh_token_lifetime),
                    nonce=refresh_token_request.refresh_token.nonce,
                    language=token_request.language,
                )
            )
        else:
            num_used = refresh_token.num_used + 1
            await self._refresh_token_service.update(
                refresh_token.id,
                UpdateRefreshToken(num_used=num_used, last_used_at=now),
            )

        return TokenResponse(
            token_type="Bearer",
            expires_in=self._short_token_lifetime,
            access_token=access_token,
            id_token=id_token,
            refresh_token=str(refresh_token.id),
            tenant_id=str(refresh_token_request.tenant_id),
            scope=standart_scope,
            api_scopes=api_scopes,
            nonce=refresh_token_request.refresh_token.nonce,
            language=token_request.language,
        )

    async def create_client_credentials(
        self, token_request: TokenRequest
    ) -> TokenResponse:
        """AuthorizeResponse oluşturur."""
        auth_code_request: ClientCredentialsTokenRequest = token_request  # type: ignore
        client = await self._messenger.get_client_by_client_id(
            str(auth_code_request.client.client_id)
        )
        api_scopes: List[str] = await self._messenger.client_api_scope_get(
            str(client["id"]), str(auth_code_request.tenant_id)
        )
        standart_scope = "openid profile email"
        create_token = ClientCredentialsToken(
            client_id=auth_code_request.client.client_id,
            tenant_id=auth_code_request.tenant_id,
        )
        access_token = await self._token_service.create_access_token_client_credentials(
            create_token, standart_scope, api_scopes, self._long_token_lifetime
        )

        return TokenResponse(
            token_type="Bearer",
            expires_in=self._long_token_lifetime,
            access_token=access_token,
            tenant_id=str(auth_code_request.tenant_id),
            scope=standart_scope,
            api_scopes=api_scopes,
        )

    async def create_implicit_response(
        self, token_request: TokenRequest
    ) -> TokenResponse:
        return TokenResponse(
            expires_in=3600,
            access_token="access_token",
            id_token="id_token",
            refresh_token="refresh_token",
            tenant_id="sdasda",
            scope="dsada",
            nonce="dsada",
            api_scopes=[],
            language="tr",
        )

    async def create_hybrid_response(
        self, token_request: TokenRequest
    ) -> TokenResponse:
        return TokenResponse(
            expires_in=3600,
            access_token="access_token",
            id_token="id_token",
            refresh_token="refresh_token",
            tenant_id="sdasda",
            scope="dsada",
            nonce="dsada",
            api_scopes=[],
            language="tr",
        )
