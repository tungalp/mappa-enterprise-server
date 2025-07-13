

from mapa.spatial.constant import OperatorType
from pydantic import BaseModel


class FilterParams(BaseModel):
    """FilterParams Modeli"""

    operator: OperatorType
    key: str
    value: str
