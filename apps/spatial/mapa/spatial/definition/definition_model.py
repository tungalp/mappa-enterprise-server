from typing import Any, List
from uuid import UUID

from mapa.spatial.constant import DataType
from mapa.spatial.models.field_params_model import FieldParams
from mapa.spatial.models.filter_params_model import FilterParams
from mapa.spatial.models.style_params_model import StyleParams
from mapa.spatial.models.topology_rules_params_model import TopologyRulesParams
from pydantic import BaseModel

#  code : arcgis ve geoserver için ortak bir alandır. wms den katman bilgileri getirildiğinde o an ki katmanın index bilgisi olarak tutulmaktadır.
#  timer : time slider widgeti için konulmuştur. Katmanın time slider özelliği var mı yok mu sorusuna cevap verir.
#  is_attribute_panel : ilgili katmanın attribute panel özelliği var mı yok mu sorusuna cevap verir.
#  data_type : Katmanın raster mı vector mu olduğunu belirler
#  key_field : Katmanın anahtar alan ihtiyaçını karşılar
#  edit_snap_scale : snap yapmaya başlayabileceği değerdir
#  type_name : external bir katman ise workspace_name:layer_name - adhoc ise schema_name.layer_name olarak tanımlanmalıdır
#  organization_geo_constraint : organizasyondan gelen geo olanının katman bazlı bir kısıt olup olmayacağı bilgisidir



class Definition(BaseModel):
    """Definition Modeli"""
    id: UUID
    title: str | None = None
    default_extent: str | None = None
    max_scale: int | None = None
    min_scale: int | None = None
    opacity: float | None = None

    timer: bool | None = None
    is_attribute_panel: bool | None = None
    is_base_layer: bool | None = None
    organization_geo_constraint: bool | None = None

    edit_snap_scale: int | None = None
    data_type: DataType
    key_field: str
    type_name: str
    target_namespace: str | None = None

    style_params: StyleParams | None = None
    topology_rules_params: List[TopologyRulesParams] | None = None
    filter_params: List[FilterParams] | None = None
    field_params: List[FieldParams] | None = None


class CreateDefinition(BaseModel):
    title: str | None = None
    default_extent: str | None = None
    max_scale: int | None = None
    min_scale: int | None = None
    opacity: float | None = None
    timer: bool | None = None
    is_attribute_panel: bool | None = None
    organization_geo_constraint: bool | None = None
    is_base_layer: bool | None = None

    edit_snap_scale: int | None = None
    data_type: DataType
    key_field: str
    type_name: str
    target_namespace: str | None = None

    style_params: Any | None = None
    topology_rules_params: List[TopologyRulesParams] | None = None
    filter_params: List[FilterParams] | None = None
    field_params: List[FieldParams] | None = None


class UpdateDefinition(BaseModel):
    title: str | None = None
    default_extent: str | None = None
    max_scale: int | None = None
    min_scale: int | None = None
    opacity: float | None = None
    timer: bool | None = None
    is_attribute_panel: bool | None = None
    organization_geo_constraint: bool | None = None
    is_base_layer: bool | None = None

    edit_snap_scale: int | None = None
    data_type: DataType
    key_field: str
    type_name: str
    target_namespace: str | None = None

    style_params: Any | None = None
    topology_rules_params: List[TopologyRulesParams] | None = None
    filter_params: List[FilterParams] | None = None
    field_params: List[FieldParams] | None = None


class UpdateAllDefinition(BaseModel):
    title: str | None = None
