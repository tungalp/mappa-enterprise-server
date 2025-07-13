from typing import Dict, List, Any
from pydantic import BaseModel

class SoapInputModel(BaseModel):
    """SoapInputModel Modeli"""

    params: Any | None = None
    optional: bool | None = None
    type: str | None = None
    name: str | None = None
    
class SoapMethodModel(BaseModel):
    """SoapMethodModel Modeli"""
    
    method_name: str
    inputs: List[SoapInputModel]
    
class SoapBindingModel(BaseModel):
    """SoapBindingsModel Modeli"""
    
    binding_name: str
    methods: Dict[str, Any]
    
class SoapServiceModel(BaseModel):
    """SoapServiceModel Modeli"""
    
    service_name: str
    bindings: Dict[str, Any]
    
class SoapModel(BaseModel):
    """SoapModel Modeli"""
    
    services: Dict[str, Any]

class SoapEndpoint(BaseModel):
    """SoapEndpoint Modeli"""
    
    endpoint: str | None = None
    connection_info_id: str | None = None
    wsdl_endpoint: str
