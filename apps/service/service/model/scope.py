from typing import Any, Dict
from pydantic import BaseModel


class ServiceScope(BaseModel):
    """Gelen verilerin toplandığı kapsam"""

    header: Dict[str, str]
    body: Any | Dict[str, str]
    status_code: int = 0
    path: Dict[str, Any] | None = None
    query: Dict[str, Any] | None = None
    context: Dict[str, Any] | None = None