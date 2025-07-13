from typing import Any, Dict, List
from uuid import UUID

from mapa.spatial.definition.definition_model import Definition
from mapa.spatial.layer.layer_model import Layer
from mapa.spatial.layer_hook.layer_hook_model import LayerHook
from pydantic import BaseModel

# layer_hooks : layer ve definition bilgilerinin birleştiği yer olarak ilgili katman tanımının hook bilgileri liste halinde buraya set edilmektedir.


class LayerDefinition(BaseModel):
    """LayerDefinition Modeli"""
    id: UUID
    layer_id: UUID
    layer: Layer | None = None

    definition_id: UUID | None = None
    definition: Definition | None = None
    layer_hooks: List[LayerHook] | None = None
    layer_hooks_gateway_params: Any | None = None


class CreateLayerDefinition(BaseModel):
    layer_id: UUID
    definition_id: UUID | None = None


class UpdateLayerDefinition(BaseModel):
    layer_id: UUID
    definition_id: UUID | None = None


class UpdateAllLayerDefinition(BaseModel):
    pass
