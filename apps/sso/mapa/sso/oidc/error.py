"""Hata sınıfları
"""

from mapa.sso.constants import AuthorizationErrors, AuthorizeErrors, TokenErrors


class OidcError():
    """Genel OpenID hata sınıfı
    """

    def __init__(self, error: str, status_code: int = 200, error_description: str | None = None, error_uri: str | None = None) -> None:
        self.status_code = status_code
        self.error = error
        # TODO (kgulenc) Bu kısma dil seçeneği eklenecek
        self.error_description = error if not error_description else error_description
        self.error_uri = error_uri


class InsecureTransportError(OidcError):
    """InsecureTransportError"""

    def __init__(self) -> None:
        super().__init__(AuthorizeErrors.INSECURE_TRANSPORT)


class InvalidRequestError(OidcError):
    """InvalidRequestError"""

    def __init__(self, error_description: str) -> None:
        super().__init__(
            AuthorizeErrors.INVALID_REQUEST,
            error_description=error_description
        )


class InvalidClientError(OidcError):
    """InvalidClientError"""

    def __init__(self) -> None:
        super().__init__(AuthorizeErrors.INVALID_CLIENT)


class InvalidGrantError(OidcError):
    """InvalidGrantError"""

    def __init__(self) -> None:
        super().__init__(TokenErrors.INVALID_GRANT)


class UnauthorizedClientError(OidcError):
    """UnauthorizedClientError"""

    def __init__(self) -> None:
        super().__init__(TokenErrors.UNAUTHORIZED_CLIENT)


class UnsupportedGrantTypeError(OidcError):
    """UnsupportedGrantTypeError"""

    def __init__(self) -> None:
        super().__init__(TokenErrors.UNSUPPORTED_GRANT_TYPE)


class InvalidScopeError(OidcError):
    """InvalidScopeError"""

    def __init__(self) -> None:
        super().__init__(TokenErrors.INVALID_SCOPE)


class AccessDeniedError(OidcError):
    """AccessDeniedError"""

    def __init__(self) -> None:
        super().__init__(TokenErrors.ACCESS_DENIED)


class MissingAuthorizationError(OidcError):
    """MissingAuthorizationError"""

    def __init__(self) -> None:
        super().__init__(AuthorizationErrors.MISSING_AUTHORIZATION, 401)


class UnsupportedResponseTypeError(OidcError):
    """UnsupportedResponseTypeError"""

    def __init__(self) -> None:
        super().__init__(AuthorizeErrors.UNSUPPORTED_RESPONSE_TYPE, 401)


class UnsupportedResponseModeError(OidcError):
    """UnsupportedResponseModeError"""

    def __init__(self) -> None:
        super().__init__(AuthorizeErrors.UNSUPPORTED_RESPONSE_MODE, 401, "")


class UnsupportedTokenTypeError(OidcError):
    """UnsupportedTokenTypeError"""

    def __init__(self) -> None:
        super().__init__(TokenErrors.UNSUPPORTED_TOKEN_TYPE, 401)


class MissingCodeError(OidcError):
    """MissingCodeException"""

    def __init__(self) -> None:
        super().__init__(TokenErrors.MISSING_CODE)


class MissingTokenError(OidcError):
    """MissingTokenException"""

    def __init__(self) -> None:
        super().__init__(TokenErrors.MISSING_TOKEN)


class MissingTokenTypeError(OidcError):
    """MissingTokenTypeException"""

    def __init__(self) -> None:
        super().__init__(TokenErrors.MISSING_TOKEN_TYPE)


class MismatchingStateError(OidcError):
    """MismatchingStateException"""

    def __init__(self) -> None:
        super().__init__(TokenErrors.MISMATCHING_STATE)


class LoginRequiredError(OidcError):
    """LoginRequiredError"""

    def __init__(self) -> None:
        super().__init__(AuthorizeErrors.LOGIN_REQUIRED)


class ConsentRequiredError(OidcError):
    """ConsentRequiredError"""

    def __init__(self) -> None:
        super().__init__(AuthorizeErrors.CONSENT_REQUIRED)


class AccountSelectionRequiredError(OidcError):
    """AccountSelectionRequiredError"""

    def __init__(self) -> None:
        super().__init__(AuthorizeErrors.ACCOUNT_SELECTION_REQUIRED)
