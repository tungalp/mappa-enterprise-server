from datetime import datetime
from typing import Any, Dict
from uuid import UUID
from mapa.sso.auth.auth_util_service import AuthUtilService
from mapa.sso.authorization_code.authorization_code_service import (
    AuthorizatioCodeService,
)
from mapa.sso.constants import (
    AuthorizeErrors,
    CodeChallengeMethods,
    ResponseTypes,
    TokenErrors,
)
from mapa.sso.oidc.end_points.token import TokenEndpoint
from mapa.sso.oidc.error import (
    InvalidClientError,
    InvalidRequestError,
    MissingCodeError,
    MissingTokenError,
    UnauthorizedClientError,
    UnsupportedGrantTypeError,
)
from mapa.sso.oidc.validation.token_request import (
    AuthorizationCodeTokenRequest,
    ClientCredentialsTokenRequest,
    RefreshTokenTokenRequest,
    TokenRequest,
)
from mapa.sso.oidc.validation.validation_result import ValidationResult
from mapa.sso.refresh_token.refresh_token_service import RefreshTokenService
from mapa.sso.user_session.user_session_service import UserSessionService
from mapa.sso.user_session_client.user_session_client_service import (
    UserSessionClientService,
)
from mapa.sso.constants import GrantTypes, LevelTypes
from mapa.sso.messaging.producer.service_messenger import ServiceMessenger

class TokenEndPointValidator:
    """Token servis metoduna gelen isteğine ait parametreleri doğrular."""

    grant_types = dict(
        {
            ResponseTypes.CODE: GrantTypes.AUTHORIZATION_CODE,
            ResponseTypes.TOKEN: GrantTypes.IMPLICIT,
            ResponseTypes.IDTOKEN: GrantTypes.IMPLICIT,
            ResponseTypes.IDTOKEN_TOKEN: GrantTypes.IMPLICIT,
            ResponseTypes.CODE_IDTOKEN: GrantTypes.HYBRID,
            ResponseTypes.CODE_TOKEN: GrantTypes.HYBRID,
            ResponseTypes.CODE_IDTOKEN_TOKEN: GrantTypes.HYBRID,
        }
    )

    def __init__(
        self,
        authorization_code_service: AuthorizatioCodeService,
        user_session_service: UserSessionService,
        refresh_token_service: RefreshTokenService,
        user_session_client_service: UserSessionClientService,
        util_service: AuthUtilService,
        messenger: ServiceMessenger
    ) -> None:
        self._authorization_code_service = authorization_code_service
        self._user_session_service = user_session_service
        self._refresh_token_service = refresh_token_service
        self._user_session_client_service = user_session_client_service
        self._util_service = util_service
        self._messenger = messenger

    async def validate(
        self, token_endpoint: TokenEndpoint
    ) -> ValidationResult[TokenRequest]:
        """Token servis metoduna gelen parametreleri doğrular"""

        result: Dict[str, Any] = {
            "grant_type": token_endpoint.grant_type,
        }

        # Client
        client = await self._messenger.get_client_by_client_id(token_endpoint.client_id)
        if not client:
            return ValidationResult(None, error=InvalidClientError())
        result["client"] = client

        # Client ın istenen grant type i desteklemesi gerekir
        grant_type = result["grant_type"]
        if not grant_type in client["grant_types"]:
            return ValidationResult(None, error=UnsupportedGrantTypeError())

        if grant_type == GrantTypes.AUTHORIZATION_CODE:
            return await self._validate_authorization_code(result, token_endpoint)
        if grant_type == GrantTypes.REFRESH_TOKEN:
            return await self._validate_refresh_token(result, token_endpoint)
        elif grant_type == GrantTypes.PASSWORD:
            return await self._validate_password(result, token_endpoint)
        elif grant_type == GrantTypes.CLIENT_CREDENTIALS:
            return await self._validate_client_credentials(result, token_endpoint)
        else:
            return ValidationResult(None, error=UnsupportedGrantTypeError())

    async def _validate_authorization_code(
        self, result: Dict[str, Any], token_endpoint: TokenEndpoint
    ) -> ValidationResult[TokenRequest]:
        result["redirect_uri"] = token_endpoint.redirect_uri
        result["code_verifier"] = token_endpoint.code_verifier
        result["client_secret"] = token_endpoint.client_secret

        # Code
        auth_code = await self._authorization_code_service.get_by_code(
            token_endpoint.code
        )
        if not auth_code:
            return ValidationResult(None, error=MissingCodeError())
        # Code daha önceden kullanılmışsa hata verilir.
        if auth_code.used:
            return ValidationResult(
                None,
                error=InvalidRequestError(
                    error_description="code can not be used more than one time"
                ),
            )
        # Code un geçerlik süresi geçmişse hata verilir.
        if auth_code.expired_at < datetime.now():
            return ValidationResult(
                None,
                error=InvalidRequestError(error_description=TokenErrors.MISSING_CODE),
            )
        # authorize ile gönderilen redirect_uri ile token aynı olmalıdır.
        if auth_code.redirect_uri != result["redirect_uri"]:
            return ValidationResult(
                None,
                error=InvalidRequestError(
                    error_description=AuthorizeErrors.INVALID_REDIRECT_URI
                ),
            )
        result["code"] = auth_code

        # Session
        user_session = await self._user_session_service.get(auth_code.user_session_id)
        if user_session:
            if not user_session.authenticated:
                return ValidationResult(
                    None,
                    error=InvalidRequestError(
                        error_description=AuthorizeErrors.ACCESS_DENIED
                    ),
                )
            if user_session.expired_at < datetime.now():
                return ValidationResult(
                    None,
                    error=InvalidRequestError(
                        error_description=AuthorizeErrors.ACCESS_DENIED
                    ),
                )
        else:
            return ValidationResult(
                None,
                error=InvalidRequestError(
                    error_description=AuthorizeErrors.SESSION_NOT_FOUND
                ),
            )
        result["user_session"] = user_session

        # Audience
        if token_endpoint.audience:
            result["audience"] = token_endpoint.audience
        else:
            result["audience"] = auth_code.audience

        client = result["client"]

        # Tenant
        tenant_id = await self._find_tenant_id(client, auth_code.user_session_id)
        if tenant_id:
            result["tenant_id"] = str(tenant_id)
        else:
            return ValidationResult(
                None,
                error=InvalidRequestError(
                    error_description="Tenant id not found for client"
                ),
            )

        # PKCE, code verifier ve code challange
        if client["require_pkce"]:
            if not result["code_verifier"]:
                return ValidationResult(
                    None,
                    error=InvalidRequestError(
                        error_description="Client requires PKCE but code verifier not found"
                    ),
                )
            if not auth_code.code_challenge:
                return ValidationResult(
                    None,
                    error=InvalidRequestError(
                        error_description="Client requires PKCE but code challenge not found"
                    ),
                )

        # Client credential kontrol
        if client["require_pkce"]:
            # code verifier kontrol
            code_verifier: str = str(result["code_verifier"])
            if auth_code.code_challenge_method == CodeChallengeMethods.SHA256:
                code_challenge = self._util_service.generate_code_challenge(
                    code_verifier
                )
            else:
                code_challenge = code_verifier
            if auth_code.code_challenge != code_challenge:
                return ValidationResult(None, UnauthorizedClientError())
        else:
            # Eğer client token endpoint metodlarından birini destekliyorsa client secret kontrol edilir
            if client["token_endpoint_auth_method"]:
                if client["client_secret"] != result["client_secret"]:
                    return ValidationResult(None, error=UnauthorizedClientError())
        result["client"] = client

        return ValidationResult(AuthorizationCodeTokenRequest(**result))

    async def _validate_refresh_token(
        self, result: Dict[str, Any], token_endpoint: TokenEndpoint
    ) -> ValidationResult[TokenRequest]:
        client = result["client"]

        # Eğer client token endpoint metodlarından birini destekliyorsa client secret kontrol edilir
        if client["token_endpoint_auth_method"]:
            if client["client_secret"] != result["client_secret"]:
                return ValidationResult(None, error=UnauthorizedClientError())

        # Refresh Token
        refresh_token = await self._refresh_token_service.get(
            token_endpoint.refresh_token
        )
        if not refresh_token:
            return ValidationResult(None, error=MissingTokenError())

        # Refresh token aktif değilse hata verilir.
        if not refresh_token.is_active:
            return ValidationResult(
                None, InvalidRequestError(error_description=TokenErrors.INVALID_TOKEN)
            )

        # Refresh token zaman aşımı olduysa
        if refresh_token.expired_at < datetime.now():
            return ValidationResult(
                None,
                error=InvalidRequestError(error_description=TokenErrors.EXPIRED_TOKEN),
            )
        result["refresh_token"] = refresh_token

        # Session
        user_session = await self._user_session_service.get(
            refresh_token.user_session_id
        )
        if user_session:
            if not user_session.authenticated:
                return ValidationResult(
                    None,
                    error=InvalidRequestError(
                        error_description=AuthorizeErrors.ACCESS_DENIED
                    ),
                )
            if user_session.expired_at < datetime.now():
                return ValidationResult(
                    None,
                    error=InvalidRequestError(
                        error_description=AuthorizeErrors.ACCESS_DENIED
                    ),
                )
        else:
            return ValidationResult(
                None,
                error=InvalidRequestError(
                    error_description=AuthorizeErrors.SESSION_NOT_FOUND
                ),
            )
        result["user_session"] = user_session

        # Audience
        if token_endpoint.audience:
            result["audience"] = token_endpoint.audience
        else:
            result["audience"] = refresh_token.audience

        # Tenant
        tenant_id = await self._find_tenant_id(client, refresh_token.user_session_id)
        if tenant_id:
            result["tenant_id"] = str(tenant_id)
        else:
            return ValidationResult(
                None,
                error=InvalidRequestError(
                    error_description="Tenant id not found for client"
                ),
            )

        return ValidationResult(RefreshTokenTokenRequest(**result))

    async def _validate_password(
        self, result: Dict[str, Any], token_endpoint: TokenEndpoint
    ) -> ValidationResult[TokenRequest]: ...

    async def _validate_client_credentials(
        self, result: Dict[str, Any], token_endpoint: TokenEndpoint
    ) -> ValidationResult[TokenRequest]:
        client = result["client"]
        # Eğer client token endpoint metodlarından birini destekliyorsa client secret kontrol edilir
        if client["token_endpoint_auth_method"]:
            if client["client_secret"] != result["client_secret"]:
                return ValidationResult(None, error=UnauthorizedClientError())

        # Tenant
        tenant_id = await self._find_tenant_id(client, None)
        if tenant_id:
            result["tenant_id"] = str(tenant_id)
        else:
            return ValidationResult(
                None,
                error=InvalidRequestError(
                    error_description="Tenant id not found for client"
                ),
            )

        # Eğer client token endpoint metodlarından birini destekliyorsa client secret kontrol edilir
        if client["token_endpoint_auth_method"]:
            if client["client_secret"] != result["client_secret"]:
                return ValidationResult(None, error=UnauthorizedClientError())
        result["client"] = client

        return ValidationResult(ClientCredentialsTokenRequest(**result))

    async def _find_tenant_id(
        self, client, user_session_id: UUID | None
    ) -> UUID | None:
        tenant_id: UUID | None = None
        # Tenant
        if client["level_type"] == LevelTypes.FIRST_PARTY and user_session_id is not None:
            # Eğer client first party ise kullanıcının login ilgili client daki oturumundan tenant alınır.
            # ThirdParty client lar için client ın tenantı kullanılır.
            user_session_client = (
                await self._user_session_client_service.find_by_client(
                    user_session_id, client["id"]
                )
            )
            if user_session_client:
                tenant_id = user_session_client.tenant
        else:
            # ThirdParty client lar için client ın tenantı kullanılır.
            tenant_client = await self._messenger.tenant_client_get_client_id(
                str(client["id"])
            )
            if tenant_client:
                tenant_id = tenant_client["tenant_id"]
        return tenant_id
