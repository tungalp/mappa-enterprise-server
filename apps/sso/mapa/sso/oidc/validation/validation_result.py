from typing import Generic, TypeVar

from mapa.sso.oidc.error import OidcError


T = TypeVar('T')


class ValidationResult(Generic[T]):
    """Gelen doğrulama sonuç sınıfı
    """
    def __init__(self, result: T | None = None, error: OidcError | None = None) -> None:
        super().__init__()
        self.result = result
        self.error = error
