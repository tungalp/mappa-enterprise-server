import uuid
from mapa.gateway.gateway_api.gateway_api_entity import GatewayApiEntity
from mapa.gateway.integration.integration_entity import IntegrationEntity
from mapa.gateway.integration.integration_model import SoapConnection
from mapa.gateway.route.route_entity import RouteEntity
from mapa.gateway.constant import IntegrationTypes
from mapa.gateway.soap.soap_model import SoapInputModel

tenant_id = uuid.UUID("10a2238f-4d1e-4626-9f3c-799d3ef5e96d")
user_id = uuid.UUID("7175e67d-0ddc-4c96-a167-c3f3ef72de5a")

soap_api_name = str("soap-api")
soap_api_id = uuid.UUID("abba94fa-9743-48c2-b8d4-0f24e72ab95c")
soap_api = GatewayApiEntity(
    id = soap_api_id,
    tenant_id = tenant_id,
    name = soap_api_name,
    description = "soap api description",
    path = "soap",
    identifier = "http://gateway/test/soap"
)

# Multiple
soap_multiple_integration_id = uuid.UUID("f0dcc091-1d28-4663-9a72-b30d4d9ad862")
soap_multiple_integration = IntegrationEntity(
    id = soap_multiple_integration_id,
    tenant_id = tenant_id,
    name = "Soap Multiple Integration",
    description = "Soap Multiple Integration",
    context={},
    connection = SoapConnection(
        endpoint="http://host.docker.internal:5123/Service.asmx",
        wsdl_endpoint="http://host.docker.internal:5123/Service.asmx",
        method="MultipleInputModel",
        inputs=[SoapInputModel(name="str_param",optional=True,type="xsd:string"),
                SoapInputModel(name="int_param",optional=True,type="xsd:int"),
                SoapInputModel(name="inputModel",optional=True,type="ns0:ComplexModelInput")]
    ).model_dump(),
    gateway_api_id = soap_api_id,
    type=IntegrationTypes.SOAP_BACKEND
)



soap_multiple_route_id = uuid.UUID("c55a60fd-29f5-4269-86bd-068b01cd5bff")
soap_multiple_route = RouteEntity(
    id = soap_multiple_route_id,
    tenant_id = tenant_id,
    description = "Soap Multiple Route",
    path = "multiple/{str_param}",
    scope = "openid",
    gateway_api_id = soap_api_id,
    integration_id = soap_multiple_integration_id,
    method_type = "POST"
)

instances = [
    soap_api,
    soap_multiple_integration, soap_multiple_route
]
