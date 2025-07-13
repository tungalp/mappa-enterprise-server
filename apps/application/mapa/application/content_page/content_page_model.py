from datetime import datetime
from typing import List, Optional, Any
from uuid import UUID
from pydantic import BaseModel
from mapa.application.constants import ContentPageType
from nanoid import generate


class ContentPage(BaseModel):
    """ContentPage Modeli"""
    id: UUID
    type: str = ContentPageType.PAGE
    name: str
    title: str
    description:  str | None = None
    scope: str | None = None
    designer_schema: Any | None = None
    path:  str | None = None
    query:  str | None = None
    app_id: UUID


class CreateContentPage(BaseModel):
    type: str = ContentPageType.PAGE
    name: str
    title: str
    description: str | None = None
    scope: str | None = None
    designer_schema: Any | None = None
    path:  str | None = None
    query:  str | None = None
    app_id: UUID


class UpdateContentPage(BaseModel):
    name: str
    title: str
    description: str | None = None
    scope: str | None = None
    designer_schema: Any | None = None
    path:  str | None = None
    query:  str | None = None


class UpdateAllContentPage(UpdateContentPage):
    pass
