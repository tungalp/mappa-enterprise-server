from uuid import UUID

from pydantic import BaseModel


class Reference(BaseModel):
    """Reference Modeli"""
    id: UUID
    epsgcode: str
    wkid: str
    wkt: str
    projcs: str
    name: str


class CreateReference(BaseModel):
    epsgcode: str
    wkid: str
    wkt: str
    projcs: str
    name: str


class UpdateReference(BaseModel):
    epsgcode: str
    wkid: str
    wkt: str
    projcs: str
    name: str


class UpdateAllReference(BaseModel):
    pass
