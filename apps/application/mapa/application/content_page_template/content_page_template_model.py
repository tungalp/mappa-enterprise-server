from typing import Any
from uuid import UUID
from pydantic import BaseModel
from mapa.application.constants import ContentPageType

class ContentPageTemplate(BaseModel):
    """ContentPage Modeli"""
    id: UUID
    type: str = ContentPageType.PAGE
    name: str
    title: str
    description:  str | None = None
    designer_schema: Any | None = None

class CreateContentPageTemplate(BaseModel):
    type: str = ContentPageType.PAGE
    name: str
    title: str
    description: str | None = None
    designer_schema: Any | None = None


class UpdateContentPageTemplate(BaseModel):
    name: str
    title: str
    description: str | None = None
    designer_schema: Any | None = None

class UpdateAllContentPageTemplate(UpdateContentPageTemplate):
    pass

