from uuid import UUID

from mapa.spatial.constant import HookOperationType, MapWidgetType
from pydantic import BaseModel


class LayerHook(BaseModel):
    """LayerHook Modeli"""

    id: UUID
    route_id: UUID
    layer_definition_id: UUID
    widget_name: MapWidgetType
    hook_operation_type: HookOperationType


class CreateLayerHook(BaseModel):
    route_id: UUID
    layer_definition_id: UUID
    widget_name: MapWidgetType
    hook_operation_type: HookOperationType


class UpdateLayerHook(BaseModel):
    route_id: UUID
    layer_definition_id: UUID
    widget_name: MapWidgetType
    hook_operation_type: HookOperationType


class UpdateAllLayerHook(BaseModel):
    pass
