from datetime import datetime
from typing import List, Optional, Any
from uuid import UUID
from pydantic import BaseModel
from nanoid import generate

class App(BaseModel):
    """App Modeli"""
    id: UUID
    name: str
    code: str
    title: str
    description: str | None = None
    logo: str | None = None
    menu: Any | None = None
    translation: Any | None = None
    client_id: str | None = None
    api_id: UUID | None = None
    logout_uri: str | None = None
    return_uri: str | None = None
    client_secret: str | None = None
    identifier: str
    tenant_id: UUID
    content_page: Any | None = None
    ordr: int
    # TODO: Alt kısım açılınca tenant izolasyonu çalışmıyor :) (13.07.23)
    # client: Any | None = None
    # api: Any | None = None


class CreateApp(BaseModel):
    name: str
    code: str
    title: str
    identifier: str
    description: str | None = None
    logo: str | None = None
    menu: Any | None = None
    translation: Any | None = None
    logout_uri: str | None = None
    return_uri: str | None = None
    client_id: str | None = None
    api_id: UUID | None = None
    client_secret: str | None = None
    ordr: int


class UpdateApp(BaseModel):
    name: str
    code: str
    title: str
    description: str | None = None
    logo: str | None = None
    menu: Any | None = None
    translation: Any | None = None
    logout_uri: str | None = None
    return_uri: str | None = None
    order: int | None = None


class UpdateAllApp(UpdateApp):
    pass


class ExportImportApp(BaseModel):
    """ExportImportApp Modeli"""
    id: UUID | None = None
    name: str | None = None
    code: str | None = None
    title: str | None = None
    description: str | None = None
    logo: str | None = None
    menu: Any | None = None
    translation: Any | None = None
    client_id: str | None = None
    api_id: UUID | None = None
    logout_uri: str | None = None
    return_uri: str | None = None
    client_secret: str | None = None
    identifier: str | None = None
    tenant_id: UUID | None = None
    client: Any | None = None
    api: Any | None = None
    content_page: Any | None = None
    ordr: int | None = None
