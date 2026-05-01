from pydantic import TypeAdapter
from typing import List, Union, Optional, Any, Dict
from enum import Enum
from uuid import UUID

class FilterOp(str, Enum):
    EQUAL = "eq"
    CONTAINS = "contains"

class FilterType(str, Enum):
    FILTER = "filter"
    AND = "and"
    OR = "or"

class Filter(TypeAdapter(Any).core_schema.__class__): # Mocking pydantic structure
    pass

from pydantic import BaseModel

class Filter(BaseModel):
    type: Optional[FilterType] = FilterType.FILTER
    field: str
    op: FilterOp
    value: Any = None

class FilterGroup(BaseModel):
    type: FilterType
    filters: List[Union[Filter, 'FilterGroup']]

class QueryArgs(BaseModel):
    limit: int = 10
    offset: int = 0
    where: Optional[List[Union[Filter, FilterGroup]]] = None

# Test with user's query
data = {"where":[{"field":"name","op":"contains","value":"adm"}],"limit":10}
try:
    qa = QueryArgs.model_validate(data)
    print("Success:", qa)
except Exception as e:
    print("Error:", e)
