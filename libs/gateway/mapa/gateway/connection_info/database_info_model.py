from datetime import datetime
from typing import List, Optional, Any
from uuid import UUID
from pydantic import BaseModel
from nanoid import generate
from mapa.gateway.integration.integration_model import Integration
from mapa.gateway.route.route_model import Route

class DatabaseInfo(BaseModel):
    """DatabaseInfo Modeli"""
    dialect: str
    username: str
    password: str
    host: str
    port: int 
    database: str
    is_success: bool | None = None

class CreateDatabaseInfo(BaseModel):
    dialect: str
    username: str
    password: str
    host: str
    port: int 
    database: str

class UpdateDatabaseInfo(BaseModel):
    dialect: str | None = None
    username: str | None = None
    password: str | None = None
    host: str | None = None
    port: int | None = None
    database: str | None = None

class UpdateAllDatabaseInfo(BaseModel):
    dialect: str | None = None
    username: str | None = None
    password: str | None = None
    host: str | None = None
    port: int | None = None
    database: str | None = None

