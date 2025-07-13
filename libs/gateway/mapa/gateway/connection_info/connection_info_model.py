from datetime import datetime
from typing import Dict, Any
from uuid import UUID
from pydantic import BaseModel

class ConnectionInfo(BaseModel):
    """ConnectionInfo Modeli"""
    
    id: UUID
    name: str
    description: str | None = None
    params: Dict[str, Any]
    type: str
    
class CreateConnectionInfo(BaseModel):
    name: str
    description: str | None = None
    params: Dict[str, Any]
    type: str

class UpdateConnectionInfo(CreateConnectionInfo):
    ...
    
class UpdateAllConnectionInfo(BaseModel):
    ...
