from typing import List
from uuid import UUID

from mapa.spatial.constant import ConnectionTypes, MapServiceTypes, RouteParamsTypes
from pydantic import BaseModel


#  route_id : gateway üzerinde tanımlanmış route bilgisidir
#  type : wms wmts wfs tiplerine sahiptir. Bu tipler doğrultusunda giden istek url de ki "RequestTypes" ve "WebServiceTypes" parametreleri değişmektedir.
class RouteParams(BaseModel):
    """RouteParams Modeli"""
    type: RouteParamsTypes
    route_id: str


#  wms ve wmts üzerinden istek yapılırken getcapabilities parametresi kullanılarak katmanın bilgileri alınmaktadır.
#  wfs üzerinden istek yapılırken de describefeaturetype parametresi kullanılarak ilgi katmanın basic-field bilgileri-geometri field ve style bilgileri alınmaktadır
class Connection(BaseModel):
    """Connection Modeli"""
    id: UUID
    name: str
    description: str | None = None
    route_params: List[RouteParams]
    type: ConnectionTypes

class CreateConnection(BaseModel):
    name: str
    description: str | None = None
    route_params: List[RouteParams]
    type: ConnectionTypes


class UpdateConnection(BaseModel):
    name: str
    route_params: List[RouteParams]
    description: str | None = None
    type: ConnectionTypes


class UpdateAllConnection(BaseModel):
    description: str | None = None
