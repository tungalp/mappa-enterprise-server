from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar('T')
class PagingResult(BaseModel, Generic[T]):
    """Sayfalama işleminden sonra dönen sınıf
    """
    total: int
    items: List[T]
    offset: int | None = None
    limit: int | None = None


class ActionResult(BaseModel, Generic[T]):
    """Güncelleme, silme gibi topluca kayıtlar üzerinde yapılan işlemlerin sonucu
    """
    items: List[T] | None = None
    success: bool
    affected: int | None = None
    message: str | None = None