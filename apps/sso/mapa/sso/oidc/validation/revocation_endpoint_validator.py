from typing import Any, Dict
from uuid import UUID
from mapa.sso.messaging.producer.service_messenger import ServiceMessenger
from mapa.sso.oidc.end_points.revocation import RevocationEndpoint
from mapa.sso.oidc.error import (
    InvalidClientError,
    MissingTokenError,
    UnauthorizedClientError,
    UnsupportedTokenTypeError,
)
from mapa.sso.oidc.validation.revocation_request import RevocationRequest
from mapa.sso.oidc.validation.validation_result import ValidationResult
from mapa.sso.refresh_token.refresh_token_service import RefreshTokenService


class RevocationEndPointValidator:
    """Revocation servis metoduna gelen isteğine ait parametreleri doğrular."""

    def __init__(
        self, refresh_token_service: RefreshTokenService, messenger: ServiceMessenger
    ) -> None:
        self._refresh_token_service = refresh_token_service
        self._messenger = messenger

    async def validate(
        self, revocation_endpoint: RevocationEndpoint
    ) -> ValidationResult[RevocationRequest]:
        """Revocation servis metoduna gelen parametreleri doğrular"""

        result: Dict[str, Any] = {
            "token": revocation_endpoint.token,
            "token_type_hint": revocation_endpoint.token_type_hint,
        }

        # Token type
        if revocation_endpoint.token_type_hint != "refresh_token":
            return ValidationResult(None, error=UnsupportedTokenTypeError())

        # Client
        client = await self._messenger.get_client_by_client_id(
            str(revocation_endpoint.client_id)
        )
        if not client:
            return ValidationResult(None, error=InvalidClientError())
        result["client"] = client

        # Client kontrolü
        if client["client_secret"] != revocation_endpoint.client_secret:
            return ValidationResult(None, error=UnauthorizedClientError())

        refresh_token = await self._refresh_token_service.get(
            UUID(revocation_endpoint.token)
        )
        if not refresh_token:
            return ValidationResult(None, error=MissingTokenError())
        result["refresh_token"] = refresh_token

        return ValidationResult(RevocationRequest(**result))
