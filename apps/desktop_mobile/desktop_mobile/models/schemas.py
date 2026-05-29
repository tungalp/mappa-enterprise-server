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
    qgis_server_wms_url: Optional[str] = None
    qgis_server_wfs_url: Optional[str] = None
    qgis_server_wmts_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def model_validate(cls, obj: Any, **kwargs) -> "MapResponse":
        # Override to dynamically calculate has_project_file and QGIS Server OGC links
        res = super().model_validate(obj, **kwargs)
        res.has_project_file = bool(res.project_file_url)
        if res.project_file_url:
            # Dynamically get bucket name from config
            bucket = "desktop-mobile"
            try:
                import os
                import pathlib
                import yaml
                current_file_path = pathlib.Path(__file__).parent.resolve()
                config_dir = current_file_path.parent / "config"
                config_files = [config_dir / "config.yml"]
                env = os.environ.get("MAPA_ENV")
                if env == "DEVELOPMENT":
                    config_files.append(config_dir / "config.dev.yml")
                else:
                    config_files.append(config_dir / "config.prod.yml")
                for file_path in config_files:
                    if file_path.exists():
                        with open(file_path, "r", encoding="utf-8") as f:
                            cfg = yaml.safe_load(f)
                            if cfg and "minio" in cfg and "bucket" in cfg["minio"]:
                                bucket = cfg["minio"]["bucket"]
            except Exception:
                pass

            # If the shared workspace file exists locally, QGIS Server can open it directly as a standard file
            import os
            local_qgs_path = f"/workspace/scratch/qgis-projects/{res.id}.qgs"
            if os.path.exists(local_qgs_path):
                project_path = local_qgs_path
            else:
                # If using the new normalized format, use the stable key, otherwise fall back to historical key
                if res.project_file_url and "project.qgz" in res.project_file_url:
                    project_path = f"/vsis3/{bucket}/maps/{res.id}/project.qgs"
                else:
                    project_path = f"/vsis3/{bucket}/{res.project_file_url.replace('.qgz', '.qgs')}"

            # Use /ows/ (with a trailing slash) to bypass internal QGIS Server Nginx 404
            base_ows = f"http://localhost:8091/ows/?MAP={project_path}"
            res.qgis_server_wms_url = f"{base_ows}&SERVICE=WMS&REQUEST=GetCapabilities"
            res.qgis_server_wfs_url = f"{base_ows}&SERVICE=WFS&REQUEST=GetCapabilities"
            res.qgis_server_wmts_url = f"{base_ows}&SERVICE=WMTS&REQUEST=GetCapabilities"
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
