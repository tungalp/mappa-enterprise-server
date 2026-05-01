from uuid import UUID
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class RoomUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    room_id: UUID
    user_id: UUID
    tenant_id: Optional[UUID]
    joined_at: datetime

class Room(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    tenant_id: Optional[UUID]
    created_at: datetime
    name: str
    foto: Optional[str]
    creator_user_id: Optional[UUID]
    updater_user_id: Optional[UUID]
    updated_at: Optional[datetime]
    
    users: List[RoomUser] = []
    is_dm: bool = False

class CreateRoom(BaseModel):
    name: str
    foto: Optional[str] = None

class UpdateRoom(BaseModel):
    name: Optional[str] = None
    foto: Optional[str] = None

class AddRoomUser(BaseModel):
    user_id: UUID
