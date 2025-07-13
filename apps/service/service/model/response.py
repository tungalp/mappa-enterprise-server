from typing import Any, Dict
from pydantic import BaseModel


class ServiceResponse(BaseModel):
    """Integration nesnesinden gelen cevap"""

    status_code: int
    response_type: str
    cookies: Dict[str, str] = {}
    headers: Dict[str, str] = {}
    context: Dict[str, Any] = {}
    body: Any | None = None
    options: Any = {}
