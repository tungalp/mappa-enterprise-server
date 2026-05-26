from pydantic import BaseModel, Field, field_validator, ConfigDict, model_validator
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import uuid

# --- Enums ---
class AccessLevel(str, Enum):
    ADMIN = 'admin'
    USER = 'user'

# --- Collection Schemas ---
class CollectionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=30)
    description: Optional[str] = Field(None, max_length=255)

class CollectionCreate(CollectionBase):
    pass

class CollectionResponse(CollectionBase):
    id: uuid.UUID
    creator: Optional[str] = None
    updater: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# --- Map Schemas ---
class MapBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    web_map_id: Optional[uuid.UUID] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty or whitespace only')
        return v.strip()

class MapCreate(MapBase):
    pass

class MapResponse(MapBase):
    id: uuid.UUID
    project_file_url: Optional[str] = None
    creator: str
    updater: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    has_project_file: bool = False

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def model_validate(cls, obj: Any, **kwargs) -> "MapResponse":
        # Override to dynamically calculate has_project_file
        res = super().model_validate(obj, **kwargs)
        res.has_project_file = bool(res.project_file_url)
        return res

# --- Layer Schemas ---
class LayerBase(BaseModel):
    name: str = Field(..., max_length=255)
    type: str = Field(..., description="kml, kmz, shp, geojson, raster formats, wms, wfs, etc.")
    tags: Optional[str] = Field(None, max_length=255)
    url_path: Optional[str] = Field(None, max_length=800)
    bucket: Optional[str] = Field(None, max_length=100)

class LayerCreate(LayerBase):
    web_layer_definition_id: Optional[uuid.UUID] = None
    qml_params: Optional[Dict[str, Any]] = None
    sld_params: Optional[Dict[str, Any]] = None
    route_params: Optional[List[Dict[str, Any]]] = None

class LayerResponse(LayerBase):
    id: uuid.UUID
    web_layer_definition_id: Optional[uuid.UUID] = None
    qml_params: Optional[Dict[str, Any]] = None
    sld_params: Optional[Dict[str, Any]] = None
    conflicts_list: Optional[Dict[str, Any]] = None
    creator: str
    updater: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    has_data_source: bool = False
    has_qml_params: bool = False
    has_sld_params: bool = False

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def model_validate(cls, obj: Any, **kwargs) -> "LayerResponse":
        res = super().model_validate(obj, **kwargs)
        # Import LayerFileType dynamically to avoid circular import issues
        from desktop_mobile.models.entities import LayerFileType
        t = res.type.lower()
        res.has_data_source = any(t == ext or t.endswith(ext) or ext.endswith(t) for ext in LayerFileType)
        res.has_qml_params = bool(res.qml_params)
        res.has_sld_params = bool(res.sld_params)
        return res

class MergedLayerResponse(LayerResponse):
    pass

class MergedMapResponse(MapResponse):
    collections: List[CollectionResponse] = []
    layers: List[MergedLayerResponse] = []

class PresignedUrlResponse(BaseModel):
    upload_url: str
    url_path: str

# --- API Key Schemas ---
class ApiKeyCreate(BaseModel):
    description: Optional[str] = Field(None, max_length=100)
    expires_at: Optional[datetime] = None

class ApiKeyResponse(BaseModel):
    id: uuid.UUID
    public_lookup_id: str
    description: Optional[str] = None
    is_active: bool
    expires_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ApiKeyPermissionBase(BaseModel):
    target_collection_id: Optional[uuid.UUID] = None
    target_map_id: Optional[uuid.UUID] = None
    target_layer_id: Optional[uuid.UUID] = None
    access_level: AccessLevel = AccessLevel.USER

class ApiKeyPermissionCreate(ApiKeyPermissionBase):
    pass

class ApiKeyPermissionResponse(ApiKeyPermissionBase):
    id: uuid.UUID
    apikey_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Token response for API Key Authentication ---
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user_id: uuid.UUID
    public_lookup_id: str

class UserPrincipal(BaseModel):
    id: uuid.UUID
    public_lookup_id: str
    auth_type: str = "token_response"
