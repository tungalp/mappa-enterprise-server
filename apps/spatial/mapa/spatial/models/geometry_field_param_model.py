
from mapa.spatial.constant import GeometryType, SridTypes
from pydantic import BaseModel


class GeometryFieldParam (BaseModel):
    """GeometryFieldParam Model"""
    type: GeometryType
    srid: str
    field_name: str
