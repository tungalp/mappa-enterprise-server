from functools import lru_cache
import json
from typing import Any, Dict
from httpx import AsyncClient as HttpxAsyncClient
from zeep import AsyncClient as ZeepAsyncClient, Settings
from zeep.wsse.username import UsernameToken
from zeep.helpers import serialize_object
from lxml import etree
import xmltodict
import logging
from mapa.core.data.json_encoder import JsonEncoder
from mapa.gateway.integration.integration_model import SoapConnection
from mapa.gateway.connection_info.connection_info_model import ConnectionInfo
from mapa.gateway.connection_info.authentication_info_model import BasicAuthAuthenticationInfo
from mapa.gateway.constant import AuthenticationInfoTypes
from service.integration_handler.integration_handler import IntegrationHandler
from service.model.async_transport import AsyncTransport
from service.model.request import ServiceRequest
from service.model.response import ServiceResponse
import requests_cache

requests_cache.install_cache('zeep_cache', expire_after=604800)
logger = logging.getLogger(__name__)

class SoapIntegrationHandler(IntegrationHandler):
    """SOAP isteklerini asenkron olarak işleyen entegrasyon sınıfı."""

    async def execute(self, service_request: ServiceRequest) -> ServiceResponse:
        if not self.integration.connection:
            raise ValueError("Connection not defined")

        conn_info = self.integration.connection_info  # type: ignore
        auth = await self._create_auth(conn_info)

        # SOAP Client oluşturma
        soap_conn = SoapConnection(**(self.integration.connection))
        timeout = (self.integration.timeout_in_millis/1000) if self.integration.timeout_in_millis is not None and (self.integration.timeout_in_millis/1000) != 0 else 10

        # Parametre işleme
        soap_params = [soap_param.name for soap_param in soap_conn.inputs]
        soap_type_any = [soap_param.name for soap_param in soap_conn.inputs if soap_param.type == "Any"]
        rest_params = {**service_request.query_params, **service_request.path_params, **service_request.body}
                    
        values = [
            etree.fromstring(xmltodict.unparse(rest_params[p], pretty=True, full_document=False)) if p in soap_type_any and rest_params.get(p) else rest_params.get(p)
            for p in soap_params
            if p is not None
        ]

        async with HttpxAsyncClient(timeout=timeout, verify=False) as async_client:
            if auth:
                async_client.auth = (auth.username, auth.password)
            settings = {
                "force_https":False,
                "strict":False
            }
            settings = Settings(**settings)
            transport = AsyncTransport(async_client)
            client = ZeepAsyncClient(wsdl=soap_conn.wsdl_endpoint, settings=settings, transport=transport, wsse=auth)

            if soap_conn.endpoint:
                client.service._binding_options.update({'address': soap_conn.endpoint})

            if service_request is not None and service_request.headers is not None:
                print('headers:',str(service_request.headers))
                client.settings.extra_http_headers=service_request.headers 

            response = await client.service[soap_conn.method](*values)

        # Yanıt işleme
        if response is None:
            return ServiceResponse(
                status_code=200 if response else 500,
                response_type="application/json",
                body={}
            )

         # Türkçe karakter sorunu olan bazı responselar içinde bu objede de değerler bulunuyor, 
        # içerideki değerleri bu şekilde json'a ekledik, (01.07.24)
        try:
            if response is not None and '_raw_elements' in response: 
                try:
                    for i in response['_raw_elements']:
                        response[i.tag]= i.text
                except Exception as ex:
                    print(ex)
                del response['_raw_elements']
        except Exception as ex:
            print(ex)
            
        # XML objelerin içinde tarih uuid gibi değerler varsa response alınıp 
        # encoderdan geçirilmeli, (01.07.24)
        
        # Not : Dönen response içerisinde xml olduğu anlaşılan bilgiler Json'a cevrilmektedir. (08.09.2024)
        for r in response:
            try:
                if isinstance(response[r], etree._Element):
                    xml_data = etree.tostring(response[r], encoding="utf-8", pretty_print=True).decode('utf-8') # type: ignore
                    json_result = self._xml_to_json_clean(xml_data)
                    response[r] = json_result
            except Exception as ex:
                print(ex)
                
        try:
            input_dict = serialize_object(response)
            response = json.loads(json.dumps(input_dict, cls=JsonEncoder))
            print('json.loads.response:',str(response))
        except Exception as ex:
            print(ex)

        service_response = ServiceResponse(
            status_code=200 if response else 500,
            response_type="application/json",
            body=response
        )
        print('service_response:',str(service_response))
        return service_response

    async def _create_auth(self, connection_info: ConnectionInfo) -> Any:
        if connection_info and connection_info.params:
            # auth type BASICAUTH ise kimlik bilgileri döndürülür.
            if connection_info.params['type'] == AuthenticationInfoTypes.BASICAUTH:
                auth: BasicAuthAuthenticationInfo = connection_info.params['auth_params']
                return UsernameToken(**auth)  # type: ignore  
              # Değilse kimlik bilgileri boş döndürülür
            else:
                return None
        return None

    def _build_headers(self, req_headers: Any) -> Dict[str, str]:
        """Header yapısını oluşturur"""
        headers = {}
        try:
            for header in req_headers:
                headers[header] = req_headers[header]
            return headers
        except Exception as ex: 
            logger.exception(f"Error in building headers: {ex}")
            return {}

    def _remove_namespace_prefixes(self, xml_string: Any) -> Any:
        """XML stringindeki namespace öneklerini kaldırır"""
        parser = etree.XMLParser(remove_blank_text=True)
        root = etree.XML(xml_string, parser)
        for elem in root.getiterator():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}', 1)[1]
        return etree.tostring(root, encoding='utf-8', pretty_print=True).decode('utf-8')

    def _xml_to_json_clean(self, xml_string: Any) -> Any:
        """XML'i JSON'a dönüştürür."""
        clean_xml = self._remove_namespace_prefixes(xml_string)
        return xmltodict.parse(clean_xml)