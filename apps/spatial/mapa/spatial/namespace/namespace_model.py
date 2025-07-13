from uuid import UUID

from pydantic import BaseModel


class Namespace(BaseModel):
    """Namespace Modeli"""
    id: UUID
    name: str
    description: str | None = None
    title: str | None = None
    identifier: str


class CreateNamespace(BaseModel):
    name: str
    description: str | None = None
    title: str | None = None
    identifier: str


class UpdateNamespace(BaseModel):
    name: str
    description: str | None = None
    title: str | None = None
    identifier: str


class UpdateAllNamespace(BaseModel):
    description: str | None = None
    title: str | None = None
