from typing import Any, Dict, List
from mapa.core.data.base_service import BaseService
import operator
from lxml import etree
from mapa.gateway.soap.soap_model import SoapBindingModel, SoapInputModel, SoapMethodModel, SoapModel, SoapServiceModel
from requests import Session
from zeep import Client
from zeep.transports import Transport
from zeep.xsd.types import ComplexType
from zeep.xsd.types.any import AnyType
from zeep.xsd.types.simple import AnySimpleType

class SoapService(BaseService):
    """Soap Servisi"""

    def __init__(self) -> None:
        super().__init__()

    async def get_soap_infos(self, soap_endpoint: str) -> List[SoapModel]:
        """Soap servisinin Servislerini, methodlarını ve inputlarını döner"""
        
        try:
            session = Session()
            session.verify = False
            session.trust_env = False
            client = Client(soap_endpoint,transport=Transport(session=session))
        except Exception as ex:
            raise ex

        wsld_list: List[SoapModel] = []
        soap = Any         # type: ignore
        
        try:
            for service in client.wsdl.services.values():
                soap : SoapModel = SoapModel(services=SoapServiceModel(service_name=service.name,bindings={}).dict())
                binding_list : List[SoapBindingModel] = []
                for port in service.ports.values():
                    operations = sorted(
                        port.binding._operations.values(),
                        key=operator.attrgetter('name'))
                    binding : SoapBindingModel = SoapBindingModel(binding_name=port.name,methods={})
                    method_list : Any = []
                    for operation in operations:                        
                        input_list = []
                        if operation.input != None:
                            elements = operation.input.body.type.elements
                            input_list = parse_elements(elements)
                            method_list.append(SoapMethodModel(method_name=operation.name,inputs = input_list))
                    binding.methods = method_list
                    binding_list.append(binding)
                soap.services['bindings'] = binding_list
            wsld_list.append(soap)    
        except Exception as ex:
            raise ex    
    
        return wsld_list


def parse_elements(elements):
    input_list = []
    print('elements:',str(elements))
    for name, element in elements:
        print('name:',str(name))
        print('element:',str(element))

        model : SoapInputModel = SoapInputModel(name= "",type= "", optional= False, params = [])
        model.optional = element.is_optional
        if element.name is not None:
            model.name = str(element.name)
        else:
            model.name = name
        
        # if hasattr(element.type, 'elements'):
        #     # Eğer element'in alt elemanları varsa, recursive olarak parse ediliyor.
        #     model.params = parse_elements(element.type.elements)
        #     model.type = 'Object'
        # elif isinstance(element.type, AnyType):
        #     # Eğer element bir 'Any' türündeyse, genel bir veri tipi olarak ele alınacak
        #     model.type = 'Any'
        #     model.params = []  # Bu durumda alt elementler olmadığını varsayıyoruz
        # else:
        #     model.type = element.type.name
        
        # Eğer element tipi ComplexType ise, complex tip olarak kabul edilir
        if isinstance(element.type, ComplexType):
            model.params = parse_elements(element.type.elements)
            model.type = 'Object'
        # Eğer element tipi SimpleType ise, primitive tip olarak kabul edilir
        elif isinstance(element.type, AnySimpleType):
            model.type = element.type.name
            model.params = []
        # Eğer elementin tipi 'AnyType' ise, genel bir veri tipi olduğu kabul ediliyor
        elif isinstance(element.type, AnyType):
            model.type = 'Any'
            model.params = []  # AnyType olduğunda alt eleman olmadığını varsayıyoruz
        else:
            # Eğer başka bir tipe sahipse, default olarak tipini alır
            model.type = element.type.name
            model.params = []
            
        input_list.append(model) 
    return input_list