from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Union
from uuid import UUID

from pydantic import BaseModel


class FilterOp(Enum):
    """Filtreler"""

    EQUAL = "eq"
    NOT_EQUAL = "ne"
    IN = "in"
    NOT_IN = "not_in"
    NULL = "null"
    NOT_NULL = "not_null"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "le"
    LIKE = "like"
    ILIKE = "ilike"
    NOT_LIKE = "not_like"
    NOT_ILIKE = "not_ilike"
    MORE_THAN = "gt"
    MORE_THAN_OR_EQUAL = "ge"
    BETWEEN = "between"
    # Spatial Operators
    BBOX = "bbox"
    EQUALS = "equals"
    DISJOINT = "disjoint"
    INTERSECTS = "intersects"
    TOUCHES = "touches"
    CROSSES = "crosses"
    WITHIN = "within"
    CONTAINS = "contains"
    OVERLAPS = "overlaps"
    RELATE = "relate"
    # Distance Operators
    DWITHIN = "dwithin"
    BEYOND = "beyond"   
    # NOT_BETWEEN
    # EXISTS
    # NOT_EXISTS
    


class FilterType(str, Enum):
    """Filtre tipleri"""

    FILTER = "filter",
    AND = "and"
    OR = "or"
    

class Filter(BaseModel):
    """Sorgu Filtesi"""

    type: FilterType | None = FilterType.FILTER
    field: str
    op: FilterOp
    value: Any | List[Any] | None = None


class FilterGroup(BaseModel):
    """Sorgu Grubu"""
    type: FilterType
    filters: List[Filter | FilterGroup]


OrderType = Literal["asc", "desc"]
class QueryArgs(BaseModel):
    """Sorgulama parametreleri"""

    limit: int = 10
    offset: int = 0
    select: List[str] | None = None
    model: List[str | Dict[str, Any]] | None = None
    where: List[Filter | FilterGroup] | None = None
    order: Dict[str, OrderType] | None = None
    
    def _serialize_filters(self, filters: List[Union[Filter, FilterGroup]]) -> List[Dict[str, Any]]:
        result = []
        for f in filters:
            if isinstance(f, Filter):
                result.append(self._serialize_object(f.model_dump()))
            elif isinstance(f, FilterGroup):
                group = f.model_dump()
                group["filters"] = self._serialize_filters(f.filters)
                result.append(group)
        return result

    def _serialize_object(self, obj: Any) -> Any:
        if isinstance(obj, BaseModel):
            return {k: self._serialize_object(v) for k, v in obj.model_dump().items()}
        elif isinstance(obj, list):
            return [self._serialize_object(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self._serialize_object(v) for k, v in obj.items()}
        elif isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, UUID):
            return str(obj)
        else:
            return obj

    def to_serialize(self) -> Dict[str, Any]:
        data = self.model_dump()
        if self.where:
            data["where"] = self._serialize_filters(self.where)
        return data