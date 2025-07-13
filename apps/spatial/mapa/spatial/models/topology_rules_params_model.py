
from mapa.spatial.constant import RuleType
from pydantic import BaseModel


class TopologyRulesParams(BaseModel):
    """TopologyRulesParams Modeli"""
    
    name: str
    destination_layer_id: str
    rule_type: RuleType
    tolerance: int | None = None
    expression: str | None = None
