from mapa.spatial.constant import RuleType
from pydantic import BaseModel


class StyleParams(BaseModel):
    """StyleParams Modeli"""
    
    name: str | None = None
    desc: str | None = None
    json: str
