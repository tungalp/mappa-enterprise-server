from datetime import datetime, timedelta
from typing import cast
from uuid import UUID
from mapa.sso.constants import GrantTypes
from mapa.sso.models import TenantUserRole
from mapa.sso.authorization_code.authorization_code_model import CreateAuthorizationCode
from mapa.sso.authorization_code.authorization_code_service import (
    AuthorizatioCodeService,
)
from mapa.sso.constants import TokenErrors
from mapa.sso.messaging.producer.service_messenger import ServiceMessenger
from mapa.sso.oidc.response_handling.authorize_error_response import (
    AuthorizeErrorResponse,
)
from mapa.sso.oidc.response_handling.authorize_response import AuthorizeResponse
from mapa.sso.oidc.validation.authorize_request import AuthorizeRequest
from mapa.sso.user_session.user_session_model import UserSession
from mapa.sso.user_session_client.user_session_client_model import (
    CreateUserSessionClient,
    UserSessionClient,
)
from mapa.sso.user_session_client.user_session_client_service import (
    UserSessionClientService,
)


class AuthorizeResponseHandler:
    """Doğrulanmış authorize isteğini işleyerek uygun dönüş
    değerini oluşturur.
    """

    def __init__(
        self,
        authorization_code_service: AuthorizatioCodeService,
        user_session_client_service: UserSessionClientService,
        messenger: ServiceMessenger,
    ) -> None:
        self._auth_code_service = authorization_code_service
        self._user_session_client_service = user_session_client_service
        self._messenger = messenger
        pass

    async def create_response(
        self, authorize_request: AuthorizeRequest
    ) -> AuthorizeResponse | AuthorizeErrorResponse:
        """Authorize servisine gelen isteği işler. Gelen isteğin durumuna göre akışları tanımlar"""
        ret_val: AuthorizeResponse | AuthorizeErrorResponse
        if authorize_request.grant_type == GrantTypes.AUTHORIZATION_CODE:
            ret_val = await self.create_authorization_code_response(authorize_request)
        elif authorize_request.grant_type == GrantTypes.IMPLICIT:
            ret_val = await self.create_implicit_response(authorize_request)
        elif authorize_request.grant_type == GrantTypes.HYBRID:
            ret_val = await self.create_hybrid_response(authorize_request)
        else:
            return AuthorizeErrorResponse(
                error=TokenErrors.INVALID_GRANT,
                error_description=",".join(
                    [res_type for res_type in authorize_request.response_types]
                ),
            )
        return ret_val

    async def create_authorization_code_response(
        self, authorize_request: AuthorizeRequest
    ) -> AuthorizeResponse:
        """AuthorizeResponse oluşturur."""
        now = datetime.now()
        create_code = CreateAuthorizationCode(
            client_id=authorize_request.client.client_id,
            user_session_id=authorize_request.user_session.id,
            user_id=authorize_request.user_session.user_id,
            scopes=authorize_request.scopes,
            redirect_uri=authorize_request.redirect_uri,
            audience=authorize_request.audience,
            nonce=authorize_request.nonce,
            code_challenge=authorize_request.code_challenge,
            code_challenge_method=authorize_request.code_challenge_method,
            code=self._auth_code_service.generate_code(),
            created_at=now,
            expired_at=now + timedelta(minutes=10),
        )
        # User için SessionClient oluşturulur
        user_session_client = await self.create_user_session_client(authorize_request)
        authorization_code = await self._auth_code_service.create(create_code)
        return AuthorizeResponse(
            code=authorization_code.code, state=authorize_request.state
        )

    async def create_implicit_response(
        self, authorize_request: AuthorizeRequest
    ) -> AuthorizeResponse: ...

    async def create_hybrid_response(
        self, authorize_request: AuthorizeRequest
    ) -> AuthorizeResponse: ...

    async def create_user_session_client(
        self, auth_request: AuthorizeRequest
    ) -> UserSessionClient:
        user_session = cast(UserSession, auth_request.user_session)
        # Daha önce bu client ile oturum açılmış mı
        user_session_client = await self._user_session_client_service.find_by_client(
            user_session.id, auth_request.client.id
        )
        # Daha önce bu client ile oturum açılmamışssa
        if not user_session_client:
            # Kullanıcının tenant ı bulunur ve bu tenant için oturum açılır.
            tenant_id = await self._find_tenant_id(user_session.user_id)
            user_session_client = await self._user_session_client_service.create(
                CreateUserSessionClient(
                    user_session_id=user_session.id,
                    client_id=auth_request.client.id,
                    tenant=tenant_id,
                    created_at=datetime.now(),
                )
            )
        else:
            # Eğer bu client için daha önceden bir oturum açılmışsa bu tenant kullanılır.
            tenant_id = user_session_client.tenant

    # TODO: tenant_user tablosundan tenant izolasyonu kaldırılarak aşağıdaki metottaki sorun düzeltildi. tekrar bakılacak. (12.07.23)
    async def _find_tenant_id(self, user_id: UUID) -> UUID:
        tenant_users = await self._messenger.find_by_user_id(str(user_id))
        tenant_user = next(
            filter(lambda x: x["role"] == TenantUserRole.OWNER, tenant_users), None
        )
        if tenant_user:
            return UUID(tenant_user["tenant_id"])
        else:
            return UUID(tenant_users[0]["tenant_id"])
