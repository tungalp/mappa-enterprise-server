from typing import Any
from pydantic import BaseModel


class IApplication(BaseModel):
    name: str


class IClient(BaseModel):
    host: str
    port: int


class IResponse(BaseModel):
    status_code: int
    body: Any | None = None


class IRequest(BaseModel):
    url: str
    path: str
    path_params: Any | None = None
    query_params: Any | None = None
    headers: Any | None = None


class IException(BaseModel):
    type: str
    message: str


class IUser(BaseModel):
    user_id: str | None = None
    tenant_id: str | None = None
    is_authenticated: bool | None = None


class ILog(BaseModel):
    rid: str
    env: str
    application: IApplication
    user: IUser | None = None
    response: IResponse | None = None
    request: IRequest | None = None
    exception: IException | None = None
    client: IClient | None = None
    completed_in: str
