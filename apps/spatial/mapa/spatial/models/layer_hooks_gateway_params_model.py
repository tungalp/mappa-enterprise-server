
from uuid import UUID
from pydantic import BaseModel
from mapa.spatial.constant import HookOperationType, MapWidgetType


# Layerın layer hook ve gateway üzerinde ki bilgilerini doldurur

class LayerHookGatewayParams(BaseModel):
    """LayerHookGatewayParams Model"""
    
    full_path: str | None = None
    endpoint: str | None = None
    method_type: str | None = None
    
    route_id: UUID | None = None
    layer_definition_id: UUID | None = None
    widget_name: MapWidgetType | None = None
    hook_operation_type: HookOperationType | None = None