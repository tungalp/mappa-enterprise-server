from typing import Any, List
from uuid import UUID
from pydantic import BaseModel
from mapa.spatial.constant import DataType
from mapa.spatial.models.field_params_model import FieldParams
from mapa.spatial.models.filter_params_model import FilterParams
from mapa.spatial.models.layer_hooks_gateway_params_model import LayerHookGatewayParams
from mapa.spatial.models.style_params_model import StyleParams
from mapa.spatial.models.topology_rules_params_model import TopologyRulesParams
from mapa.spatial.models.geometry_field_param_model import GeometryFieldParam
from mapa.spatial.models.layer_gateway_params_model import LayerGatewayParams
from mapa.spatial.connection.connection_model import Connection
from mapa.spatial.layer_hook.layer_hook_model import LayerHook

class MergeLayer(BaseModel):
    """MergeLayer Model"""

    # MapLayer Props
    id: UUID
    map_layer_name: str
    parent_id: str | None = None
    order: int
    children: Any | None = None
    
    #LayerDefinition Props
    layer_hooks: List[LayerHook] | None = None
    layer_hooks_gateway_params: List[LayerHookGatewayParams] | None = None

    # Merge Props
    title: str | None = None
    default_extent: str | None = None
    max_scale: int | None = None
    min_scale: int | None = None
    opacity: float | None = None
    timer: bool | None = None
    data_type: DataType | None = None
    key_field: str | None = None
    type_name: str | None = None
    style_params: StyleParams | None = None
    field_params: List[FieldParams] | None = None
    target_namespace: str | None = None
    
    # Layer Props
    name: str| None = None
    code: str | None = None
    description: str | None = None
    visible: bool | None = None
    connection_id: UUID | None = None
    connection: Connection | None = None
    geometry_field_param: GeometryFieldParam | None = None
    layer_gateway_params: LayerGatewayParams | None = None
    
    # Definition Props
    is_attribute_panel: bool | None = None
    organization_geo_constraint: bool | None = None
    is_base_layer: bool | None = None
    edit_snap_scale: int | None = None
    topology_rules_params: List[TopologyRulesParams] | None = None
    filter_params: List[FilterParams] | None = None
    
    # External Props
    tenant_name: str
    service_host: str



    
    