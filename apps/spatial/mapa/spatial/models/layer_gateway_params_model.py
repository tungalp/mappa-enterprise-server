
from pydantic import BaseModel


# Layerın gateway üzerinde ki bilgilerini doldurur
# Wms - Tile - Feature - Transaction ile bağlanmış 
# server_type -> arcgis / geoserver
# backend_type -> external / adhoc
class LayerGatewayParams(BaseModel):
    """LayerGatewayParams Model"""
    
    wms_path: str | None = None
    wms_endpoint: str | None = None
    wms_method_type: str | None = None
    wms_server_type: str | None = None
    wms_backend_type: str | None = None
    wms_sql: str | None = None
    wms_geometry_column: str | None = None
    wms_service_format: str | None = None
    
    tile_path: str | None = None
    tile_endpoint: str | None = None
    tile_method_type: str | None = None
    tile_server_type: str | None = None
    tile_backend_type: str | None = None
    tile_sql: str | None = None
    tile_geometry_column: str | None = None
    tile_service_format: str | None = None
    
    feature_path: str | None = None
    feature_endpoint: str | None = None
    feature_method_type: str | None = None
    feature_server_type: str | None = None
    feature_backend_type: str | None = None
    feature_sql: str | None = None
    feature_geometry_column: str | None = None
    feature_service_format: str | None = None
    
    transaction_path: str | None = None
    transaction_endpoint: str | None = None
    transaction_method_type: str | None = None
    transaction_server_type: str | None = None
    transaction_backend_type: str | None = None
    transaction_sql: str | None = None
    transaction_geometry_column: str | None = None
    transaction_service_format: str | None = None
