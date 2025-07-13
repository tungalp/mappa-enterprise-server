from typing import Any, Dict, NamedTuple
from uuid import UUID
from pydantic import BaseModel

class Address(NamedTuple):
    host: str
    port: int


class RequestContext(BaseModel):
    tenant_name: str
    tenant_id: UUID
    api_path: str
    api_id: UUID
    auth: Any
    user: Any
    

class ServiceRequest(BaseModel):
    """Integration nesnesine gönderilecek olan çözümlenmiş istek"""
    id: str
    method: str
    cookies: Dict[str, str] = {}
    client: Address | None = None
    headers: Dict[str, str] = {}
    raw_path: str
    path: str
    path_params: Dict[str, Any]
    query_string: str = ""
    query_params: Dict[str, Any] = {}
    context: Dict[str, Any] = {}
    body: Any = {}
