from typing import Any, List
from uuid import UUID

from mapa.spatial.connection.connection_model import Connection
from mapa.spatial.constant import DataType
from mapa.spatial.models.field_params_model import FieldParams
from mapa.spatial.models.geometry_field_param_model import GeometryFieldParam
from mapa.spatial.models.layer_gateway_params_model import LayerGatewayParams
from pydantic import BaseModel

from mapa.spatial.models.style_params_model import StyleParams

#  code : arcgis ve geoserver için ortak bir alandır. wms den katman bilgileri getirildiğinde o an ki katmanın index bilgisi olarak tutulmaktadır.
#  timer : time slider widgeti için konulmuştur. Katmanın time slider özelliği var mı yok mu sorusuna cevap verir.
#  layer_gateway_params : Gateway bilgilerinin tutulduğu bir model
#  data_type : Katmanın raster mı vector mu olduğunu belirler
#  key_field : Katmanın anahtar alan ihtiyaçını karşılar
#  type_name : external bir katman ise workspace_name:layer_name - adhoc ise schema_name.layer_name olarak tanımlanmalıdır


class Layer(BaseModel):
    """Layer Modeli"""
    id: UUID
    name: str
    code: str | None = None
    description: str | None = None
    title: str | None = None
    default_extent: str | None = None

    max_scale: int | None = None
    min_scale: int | None = None
    opacity: float | None = None

    timer: bool | None = None
    visible: bool | None = None

    connection_id: UUID
    connection: Connection | None = None

    field_params: List[FieldParams] | None = None
    geometry_field_param: GeometryFieldParam | None = None
    style_params: StyleParams | None = None
    
    layer_gateway_params: LayerGatewayParams | None = None
    
    data_type: DataType
    key_field: str
    type_name: str
    target_namespace: str | None = None

    
class CreateLayer(BaseModel):
    name: str
    code: str | None = None
    description: str | None = None
    title: str | None = None
    default_extent: str | None = None

    max_scale: int | None = None
    min_scale: int | None = None
    opacity: float | None = None

    timer: bool | None = None
    visible: bool | None = None

    connection_id: UUID
    data_type: DataType
    key_field: str
    type_name: str
    target_namespace: str | None = None

    field_params: List[FieldParams] | None = None
    geometry_field_param: GeometryFieldParam | None = None
    style_params: Any | None = None


class UpdateLayer(BaseModel):
    name: str
    code: str | None = None
    description: str | None = None
    title: str | None = None
    default_extent: str | None = None

    max_scale: int | None = None
    min_scale: int | None = None
    opacity: float | None = None

    timer: bool | None = None
    visible: bool | None = None

    connection_id: UUID
    data_type: DataType
    key_field: str
    type_name: str
    target_namespace: str | None = None

    field_params: List[FieldParams] | None = None
    geometry_field_param: GeometryFieldParam | None = None
    style_params: Any | None = None


class UpdateAllLayer(BaseModel):
    description: str | None = None
    title: str | None = None
    code: str | None = None
