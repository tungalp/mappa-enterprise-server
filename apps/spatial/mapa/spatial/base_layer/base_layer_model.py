from typing import List
from uuid import UUID

from mapa.spatial.constant import BaseLayerTypes
from pydantic import BaseModel

# tile_size = 256-512 değeri olabilir. Katmanın tile boyutları 256x256 yada 512x512
# tiles = tile olarak yayınlanan katmanın url bilgileri string listesinde tutar
# thumbnail = base layer olarak oluşturulan bir datanın ön izleme / küçük resim değeri


class BaseLayerConnection(BaseModel):
    name: str
    tile_size: int
    tiles: List[str]
    thumbnail: str | None = None


class BaseLayer(BaseModel):
    """BaseLayer Modeli"""
    id: UUID
    type: BaseLayerTypes
    connection: BaseLayerConnection


class CreateBaseLayer(BaseModel):
    type: BaseLayerTypes
    connection: BaseLayerConnection 


class UpdateBaseLayer(BaseModel):
    type: BaseLayerTypes
    connection: BaseLayerConnection | None = None


class UpdateAllBaseLayer(BaseModel):
    type: BaseLayerTypes
