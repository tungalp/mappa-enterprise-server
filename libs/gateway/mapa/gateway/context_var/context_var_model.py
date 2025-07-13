from typing import Any, Dict
from uuid import UUID
from pydantic import BaseModel

class ConvextVar(BaseModel):
    """ContextVar Modeli"""
    id: UUID
    key: str
    value: Any

class CreateConvextVar(BaseModel):
    key: str
    value: Any

class UpdateConvextVar(BaseModel):
    key: str
    value: Any

class UpdateAllConvextVar(BaseModel):
    value: Any
