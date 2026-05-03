from typing import Any
from uuid import UUID
from datetime import datetime

from mapa.spatial.constant import FileType
from pydantic import BaseModel, Field


class FileStore(BaseModel):
    """FileStore Modeli"""
    id: UUID
    created_at: datetime
    creator_user_id: UUID
    updater_user_id: UUID | None = None 
    updated_at: datetime | None = None 
    file_format: FileType
    file_url: str | None = None


    

class CreateFileStore(BaseModel):
    file_format: FileType
    file_url: str | None = None
    data: Any | None = Field(default=None, exclude=True)


class UpdateFileStore(BaseModel):
    file_format: FileType
    file_url: str | None = None
    data: Any | None = Field(default=None, exclude=True)




class UpdateAllFileStore(BaseModel):
    pass
