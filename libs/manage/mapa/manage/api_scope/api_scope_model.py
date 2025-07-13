from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


class ApiScope(BaseModel):
    """Api Modeli"""
    id: UUID
    name: str
    description: str
    api_id: UUID

class CreateApiScope(BaseModel):
    name: str
    description: str
    api_id: UUID


class UpdateApiScope(BaseModel):
    name: str | None = None
    description: str | None = None


class UpdateAllApiScope(UpdateApiScope):
    pass
