import json
from uuid import uuid4
from mapa.core.data.json_encoder import JsonEncoder
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.gateway.connection_info.connection_info_model import CreateConnectionInfo
from mapa.gateway.constant import ConnectionInfoTypes
from mapa.gateway.gateway_api.gateway_api_model import CreateGatewayApi, GatewayApi
from .data import generate_authorization_info_gomap,generate_route_gomap_wms,generate_route_gomap_feature_get,generate_route_gomap_feature_post, generate_gateway_api_gomap, generate_integration_external_wms_gomap,generate_integration_external_feature_gomap
from mapa.gateway.integration.integration_model import CreateIntegration, Integration
import pytest
from nanoid import generate
from mapa.gateway.route.route_model import CreateRoute, Route

@pytest.mark.asyncio
async def test_create_gomap_data(fixture):
    """Find metodunu test eder, varolan bir integration id olduğu için 200 dönmesi gerekiyor. """

    async with fixture.client() as client:
        create_gateway_api: GatewayApi = generate_gateway_api_gomap()
        create_gateway_api_response = await client.post(
            "/api/gateway/gateway_api/",
            content=json.dumps([obj.model_dump(exclude_none=True)
                               for obj in [create_gateway_api]], cls=JsonEncoder)
        )
        assert create_gateway_api_response.status_code == 201
        gateway_api_id = create_gateway_api_response.json()["items"][0]["id"]

        create_connection_info: CreateConnectionInfo = CreateConnectionInfo(
            name="gomap",
            description="test_gomap_auth",
            params=generate_authorization_info_gomap().model_dump(),
            type=ConnectionInfoTypes.AUTHENTICATION
        )
        create_connection_infos = [create_connection_info]
        connection_info_content = json.dumps([obj.model_dump(
            exclude_none=True) for obj in create_connection_infos], cls=JsonEncoder)
        create_connection_info_response = await client.post(f"/api/gateway/connection_info/", content=connection_info_content)
        assert create_connection_info_response.status_code == 201
        connection_info_id = create_connection_info_response.json()[
            "items"][0]["id"]

        # wms için integration ve route eklenir
        create_integration_wms: Integration = generate_integration_external_wms_gomap(
            gateway_api_id, connection_info_id)
        obj2 = [obj.model_dump(exclude_none=True) for obj in [create_integration_wms]]
        obj2[0]["default_route"] = False
        obj2[0]["default_route_path"] = ""
        content2 = json.dumps(obj2, cls=JsonEncoder)
        create_integration_wms_response = await client.post(
            "/api/gateway/integration/",
            content=content2)
        
        integration_wms_id = create_integration_wms_response.json()[
            "items"][0]["id"]
        

        create_route_wms: Route = generate_route_gomap_wms(gateway_api_id,integration_wms_id)
        create_route_response1 = await client.post(
            "/api/gateway/route/",
            content=json.dumps([obj.model_dump(exclude_none=True) for obj in [create_route_wms]], cls=JsonEncoder))
        
        
        # feature için integration ve route eklenir
        create_integration_feature: Integration = generate_integration_external_feature_gomap(
            gateway_api_id, connection_info_id)
        obj2 = [obj.model_dump(exclude_none=True) for obj in [create_integration_feature]]
        obj2[0]["default_route"] = False
        obj2[0]["default_route_path"] = ""
        content2 = json.dumps(obj2, cls=JsonEncoder)
        create_integration_feature_response = await client.post(
            "/api/gateway/integration/",
            content=content2)
        
        integration_feature_id = create_integration_feature_response.json()[
            "items"][0]["id"]
        
        create_route_feature_get: Route = generate_route_gomap_feature_get(gateway_api_id,integration_feature_id)
        create_route_response2 = await client.post(
            "/api/gateway/route/",
            content=json.dumps([obj.model_dump(exclude_none=True) for obj in [create_route_feature_get]], cls=JsonEncoder))
        
        create_route_feature_post: Route = generate_route_gomap_feature_post(gateway_api_id,integration_feature_id)
        create_route_response3 = await client.post(
            "/api/gateway/route/",
            content=json.dumps([obj.model_dump(exclude_none=True) for obj in [create_route_feature_post]], cls=JsonEncoder))

    assert create_route_response1.status_code == 201
    assert create_route_response2.status_code == 201
    assert create_route_response3.status_code == 201
    assert create_integration_wms_response.status_code == 201
    assert create_integration_feature_response.status_code == 201
