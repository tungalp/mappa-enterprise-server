from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional, Any, Union
from datetime import datetime
from mapa.spatial.constant import ParameterMappingTypes, SqlResultTypes
from enum import Enum

class Tenant(BaseModel):
    """Tenant"""

    id: UUID
    name: str
    user_id: UUID
    title: Optional[str]
    session_timeout: int


class SoapInputModel(BaseModel):
    """SoapInputModel Modeli"""

    params: Any | None = None
    optional: bool | None = None
    type: str | None = None
    name: str | None = None

class RequestResponseMapping(BaseModel):
    parameter_type: str
    parameter : str
    modifier : str
    value_type: str
    value : str

class ParameterMapping(BaseModel):
    """ParameterMapping Modeli"""
    id: UUID
    status_code: int = 0
    type: str = ParameterMappingTypes.REQUEST
    param_list: List[RequestResponseMapping]
    integration_id: UUID

class IntegrationTypes:
    """IntegrationTypes"""

    FUNCTIONS = "Functions"
    HTTP_BACKEND = "HTTPBackend"
    ADHOC_QUERY = "AdHocQuery"
    SOAP_BACKEND = "SoapBackend"
    FILE_BACKEND = "FileBackend"
    ELASTIC_BACKEND = "ElasticBackend"
    MONGO_QUERY = "MongoQuery"
    SPATIAL_BACKEND = "SpatialBackend"
    
    
class ConnectionInfo(BaseModel):
    """ConnectionInfo Modeli"""
    
    id: UUID
    name: str
    description: str | None = None
    params: Dict[str, Any]
    type: str
    
class Integration(BaseModel):
    """Integration Modeli"""
    id: UUID
    name: str
    gateway_api_id: UUID
    connection: Dict[str, Any]
    connection_info_id: UUID | None = None
    type: str
    description: str | None = None
    timeout_in_millis: int | None = None
    parameter_mappings: List[ParameterMapping] | None = None
    connection_info: ConnectionInfo | None = None
    gateway_api: Any | None = None
    default_route: bool | None = None
    default_route_path : str | None = None
    default_route_methods : Any | None = None
    context: Dict[str, Any] | None = None

class CreateIntegration(BaseModel):
    name: str
    description: str | None = None
    timeout_in_millis: int = 30000
    type: str
    connection: Dict[str, Any]
    connection_info_id: UUID | None = None
    gateway_api_id: UUID
    default_route: bool | None = Field(exclude=True) 
    default_route_path : str | None = Field(exclude=True)
    default_route_methods : Any | None = Field(exclude=True)
    context: Dict[str, Any] | None = None

class UpdateIntegration(BaseModel):
    name: str | None = None
    description: str | None = None
    timeout_in_millis: int = 30000
    connection: Dict[str, Any]
    connection_info_id: UUID | None = None
    context: Dict[str, Any] | None = None

class UpdateAllIntegration(BaseModel):
    description: str | None = None
    timeout_in_millis: int = 30000
    connection_info_id: UUID | None = None
    context: Dict[str, Any] | None = None

class MongoBackendConnection(BaseModel):
    """ElasticBackendConnection Type Modeli"""
    collection_name : str

class ElasticBackendConnection(BaseModel):
    """ElasticBackendConnection Type Modeli"""

    method: str
    endpoint: str
    index_name : str
    
class HttpBackendConnection(BaseModel):
    """HttpBackend Type Modeli"""

    method: str
    endpoint: str

class AdHocQueryConnection(BaseModel):
    """AdHocQuery Type Modeli"""

    sql: str
    max_count: int = 1000
    result_type: str = SqlResultTypes.MULTI
    parent_column: str = ""

class SoapConnection(BaseModel):
    """Soap Type Modeli"""

    endpoint: str
    method: str
    wsdl_endpoint: str
    inputs: List[SoapInputModel]

# Spatial Backend
class SpatialBackendType(str, Enum):
    """Backend tipleri"""

    External = "external"
    Adhoc = "adhoc"

class SpatialServiceType(str, Enum):
    """Service Tipleri"""

    WMS = "wms"
    Feature = "feature"
    Tile = "tile"
    Transaction = "transaction"
    
class SpatialServerType(str, Enum):
    """Server Tipleri"""

    Geoserver = "geoserver"
    ArcGIS = "arcgis"

class TileServiceFormat(str, Enum):
    WMTS = 'wmts'
    XYZ = 'xyz'
    TMS = 'tms'

class WmsServiceFormat(str, Enum):
    WMS_1_1_1 = 'wms_1_1_1'
    WMS_1_3_0 = 'wms_1_3_0'

class FeatureServiceFormat(str, Enum):
    WFS_2_0_0 = 'wfs_2_0_0'
    WFS_1_1_0 = 'wfs_1_1_0'
    OGC_API_1_0_1 = 'ogc_api_1_0_1'
    
class TransactionServiceFormat(str, Enum):
    WFS_T_2_0_0 = 'wfs_t_2_0_0'
    OGC_API_T_1_0_1 = 'ogc_api_t_1_0_1'

class SpatialExternalBackend(BaseModel):
    """External Backend"""
    type: Literal[SpatialBackendType.External]
    server_type: SpatialServerType
    service_format: Union[TileServiceFormat, WmsServiceFormat, FeatureServiceFormat, TransactionServiceFormat]
    method: str
    endpoint: str

class SpatialAdhocBackend(BaseModel):
    """Adhoc Backend"""
    type: Literal[SpatialBackendType.Adhoc]
    sql: str
    geometry_column: str

class SpatialConnection(BaseModel):
    """Spatial Connection type"""
    service_type: SpatialServiceType
    backend: Union[SpatialAdhocBackend, SpatialExternalBackend] = Field(..., discriminator='type')
    

class Route(BaseModel):
    """Route Modeli"""

    id: UUID
    path: str
    gateway_api_id: UUID
    method_type: str
    path: str
    created_at: datetime | None = None
    description: str | None = None
    scope: str | None = None
    query: str | None = None
    integration_id: UUID | None = None
    integration: Integration | None = None
    gateway_api: Any | None = None
    cache_timeout: int | None = None  # 60 saniye
    rate_limit: int | None = None  # 1000 adet
    rate_second: int | None = None  # 1000 saniye
    retry_count: int | None = None  # 3 kez
    retry_millisecond: int | None = None  # 500 milisaniye
    