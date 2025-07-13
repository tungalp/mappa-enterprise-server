from enum import Enum
from datetime import datetime
from typing import Dict, List, Any, Optional
from uuid import UUID
from pydantic import BaseModel

class HookType(str, Enum):
    """HookType"""

    Layer = 'Layer'
    Info = 'Info'
    AttributeTable = 'AttributeTable'


class HookOperationType(str, Enum):
    """HookOperationType"""

    GET = "GET",
    POST = "POST",
    PUT = "PUT",
    DELETE = "DELETE",


class DataType(str, Enum):
    """DataType"""

    GeoJson = 'application/json;type=geojson'
    TopoJson = 'application/json;type=topojson'
    UtfGrid = 'application/json;type=utfgrid'
    MapboxVectorTile = 'application/vnd.mapbox-vector-tile'
    Pdf = 'application/pdf'
    Gif = 'image/gif'
    Jpeg = 'image/jpeg'
    Png = 'image/png'
    Png8 = 'image/png8'
    VndJpegPng = 'image/vnd.jpeg-png'
    VndJpegPng8 = 'image/vnd.jpeg-png8'
    Tiff = 'image/tiff'
    Tiff8 = 'image/tiff8'
    GeoTiff = 'image/geotiff'
    PnGeoTiff8 = 'image/geotiff8'
    Svg = 'image/svg'


class GeometryType(str, Enum):
    """GeometryType"""
   
    Point = 'Point'
    LineString = 'LineString'
    Polygon = 'Polygon'
    MultiPoint = 'MultiPoint'
    MultiLineString = 'MultiLineString'
    MultiPolygon = 'MultiPolygon'
    Geometry = 'Geometry'


class OperatorType(str, Enum):
    """OperatorType"""

    EQUAL = "eq",
    NOT_EQUAL = "ne",
    LESS_THAN = "lt",
    LESS_THAN_OR_EQUAL = "le",
    MORE_THAN = "gt",
    MORE_THAN_OR_EQUAL = "ge",
    ILIKE = "ilike",
    LIKE = "like",
    NOT_ILIKE = "not_ilike",
    NOT_LIKE = "not_like",
    IN = "in",
    NOT_IN = "not_in",
    NULL = "null",
    NOT_NULL = "not_null",
    BETWEEN = "between"
    Contains = 'contains'
    Crosses = 'crosses'
    Disjoint = 'disjoint'
    Equals = 'equals'
    Intersects = 'intersects'
    Overlaps = 'overlaps'
    Relate = 'relate'
    Touches = 'touches'
    Within = 'within'


class RuleType(str, Enum):
    """RuleType"""

    Contains = 'contains'
    Crosses = 'crosses'
    Disjoint = 'disjoint'
    Equals = 'equals'
    Intersects = 'intersects'
    Overlaps = 'overlaps'
    Relate = 'relate'
    Touches = 'touches'
    Within = 'within'


class BaseLayerTypes(str, Enum):
    """BaseLayerTypes"""

    WebMapService = 'WebMapService'
    WebMapTileService = 'WebMapTileService'
    VectorTileService = 'VectorTileService'


class RouteParamsTypes(str, Enum):
    """RouteParamsTypes"""

    Feature = 'feature'
    Wms = 'wms'
    Tile = 'tile'
    Transaction = 'transaction'


class MapServiceTypes(str, Enum):
    """MapServiceTypes"""

    ArcGisServer = 'ArcGisServer'
    GeoServer = 'GeoServer'


class SridTypes(str, Enum):
    """SridTypes"""

    EPSG_3857 = "EPSG:3857"
    EPSG_4230 = "EPSG:4230"
    EPSG_4326 = "EPSG:4326"
    EPSG_5253 = "EPSG:5253"
    EPSG_5254 = "EPSG:5254"
    EPSG_5255 = "EPSG:5255"
    EPSG_5256 = "EPSG:5256"
    EPSG_5257 = "EPSG:5257"
    EPSG_5258 = "EPSG:5258"
    EPSG_5259 = "EPSG:5259"
    EPSG_32662 = "EPSG:32662"
    ESRI_54001 = "ESRI:54001"
    ESRI_104122 = "ESRI:104122"


class MapWidgetType(str, Enum):
    """MapWidgetType"""

    Editor = 'Editor'
    TableOfContent = 'TableOfContent'
    Measurement = 'Measurement'
    MapExport = 'MapExport'
    Info = 'Info'
    Bookmark = 'Bookmark'
    GotoXy = 'GotoXy'
    Swipe = 'Swipe'
    BaseLayerGallery = 'BaseLayerGallery'
    AttributeTable = 'AttributeTable'
    Selection = 'Selection'
    ImportExport = 'ImportExport'
    Legend = 'Legend'
    Minimap = 'Minimap'
    Search = 'Search'
    Location = 'Location'
    Navigation = 'Navigation'

class ConnectionTypes (str, Enum):
  External = "External"
  Internal = "Internal"


class ApiScopeType:   
  QUERY_BASE_LAYER = 'query:base_layer'
  EDIT_BASE_LAYER = 'edit:base_layer'
  QUERY_BOOKMARK = 'query:bookmark'
  EDIT_BOOKMARK = 'edit:bookmark'
  QUERY_CONNECTION = 'query:connection'
  EDIT_CONNECTION = 'edit:connection'
  QUERY_DEFINITION = 'query:definition'
  EDIT_DEFINITION = 'edit:definition'
  QUERY_HOOK = 'query:hook'
  EDIT_HOOK = 'edit:hook'
  QUERY_LAYER = 'query:layer'
  EDIT_LAYER = 'edit:layer'
  QUERY_LAYER_DEFINITION = 'query:layer_definition'
  EDIT_LAYER_DEFINITION = 'edit:layer_definition'
  QUERY_LAYER_HOOK = 'query:layer_hook'
  EDIT_LAYER_HOOK = 'edit:layer_hook'
  QUERY_MAP = 'query:map'
  EDIT_MAP = 'edit:map'
  QUERY_MAP_BASE_LAYER = 'query:map_base_layer'
  EDIT_MAP_BASE_LAYER = 'edit:map_base_layer'
  QUERY_MAP_LAYER = 'query:map_layer'
  EDIT_MAP_LAYER = 'edit:map_layer'
  QUERY_NAMESPACE = 'query:namespace'
  EDIT_NAMESPACE = 'edit:namespace'
  QUERY_REFERENCE = 'query:reference'
  EDIT_REFERENCE = 'edit:reference'
  
  
class SqlResultTypes:
    """Sorgu sonuçlarının dönüş şekli"""
    MULTI = "multi"
    SINGLE = "single"
    
    
class ParameterMappingTypes:
    """ParameterMappingTypes"""

    REQUEST = "request"
    RESPONSE = "response"


class ApiTypes:
    """ApiTypes"""

    HTTP = "HTTP API"
    
    
class MethodTypes:
    """MethodTypes"""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    ANY = "ANY"



class CreateGatewayApi(BaseModel):
    name: str
    path: str
    description: str | None = None
    type: str = ApiTypes.HTTP
    identifier: str
    manage_api_id: UUID | None = None
    context: Dict[str, Any] | None = None
    
    
class CreateRoute(BaseModel):
    description: str | None = None
    method_type: str = MethodTypes.GET
    path: str
    scope: str | None = None
    query: str | None = None
    gateway_api_id: UUID
    integration_id: UUID | None = None
    cache_timeout: int | None = None
    rate_limit: int | None = None
    rate_second: int | None = None
    retry_count: int | None = None
    retry_millisecond: int | None = None