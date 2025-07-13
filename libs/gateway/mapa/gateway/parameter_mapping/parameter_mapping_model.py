from datetime import datetime
from typing import List, Optional, Any, Dict
from uuid import UUID
from pydantic import BaseModel
from nanoid import generate
from mapa.gateway.constant import ParameterMappingTypes

class RequestResponseMapping(BaseModel):
    parameter_type: str
    parameter : str
    modifier : str
    value_type: str
    value : str

class ParameterMapping(BaseModel):
    """ParameterMapping Modeli"""
    id: UUID
    status_code: int = 0
    type: str = ParameterMappingTypes.REQUEST
    param_list: List[RequestResponseMapping]
    integration_id: UUID

class CreateParameterMapping(BaseModel):
    status_code: int = 0
    type: str
    param_list: Any
    integration_id: UUID

class UpdateParameterMapping(BaseModel):
    type: str
    status_code: int
    param_list: Any

class UpdateAllParameterMapping(UpdateParameterMapping):
    pass



class CreateRequestResponseMapping(BaseModel):
    parameter_type: str
    parameter : str
    modifier : str
    value_type: str
    value : str

class UpdateRequestResponseMapping(BaseModel):
    parameter_type: str
    parameter : str
    modifier : str
    value_type: str
    value : str

class  UpdateAllRequestResponseMapping(UpdateRequestResponseMapping):
    pass