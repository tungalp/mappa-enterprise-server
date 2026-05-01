from enum import Enum
from pydantic import BaseModel, TypeAdapter
from typing import List, Optional, Union, Any

class FilterOp(Enum):
    EQUAL = "eq"
    CONTAINS = "contains"

class FilterType(str, Enum):
    FILTER = "filter"

class Filter(BaseModel):
    type: Optional[FilterType] = FilterType.FILTER
    field: str
    op: FilterOp
    value: Any = None

class QueryArgs(BaseModel):
    where: Optional[List[Filter]] = None

data = {"where":[{"field":"name","op":"contains","value":"adm"}]}
try:
    qa = QueryArgs.model_validate(data)
    print("SUCCESS validation")
    print(qa.model_dump())
except Exception as e:
    print("FAILED validation")
    print(e)
