from uuid import UUID
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class MessageFile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    file_url: str
    file_name: Optional[str]
    mime_type: Optional[str]

class Message(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    tenant_id: Optional[UUID]
    created_at: datetime
    sender_id: UUID
    receiver_id: Optional[UUID]
    room_id: Optional[UUID]
    message: str
    type: str
    read1_at: Optional[datetime]
    read2_at: Optional[datetime]
    
    files: List[MessageFile] = []

class CreateMessage(BaseModel):
    receiver_id: Optional[UUID] = None
    room_id: Optional[UUID] = None
    message: str
    type: str = "text"
    file_urls: Optional[List[str]] = None
