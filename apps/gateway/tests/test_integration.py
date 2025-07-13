import json
from uuid import uuid4
from mapa.core.data.json_encoder import JsonEncoder
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.gateway.connection_info.connection_info_model import CreateConnectionInfo
from mapa.gateway.constant import ConnectionInfoTypes
from mapa.gateway.gateway_api.gateway_api_model import CreateGatewayApi
from .data import generate_authorization_info, generate_gateway_api, generate_integration
from mapa.gateway.integration.integration_model import CreateIntegration
import pytest
from nanoid import generate


@pytest.mark.asyncio
async def test_paging(fixture):
    """Find metodunu test eder """

    async with fixture.client() as client:
        query_args: QueryArgs = QueryArgs(where=[
            Filter(field="id", op=FilterOp.EQUAL, value=str(uuid4())),
        ],
            order={
            "id": "desc"
        })
        query = query_args.model_dump_json()
        query_string = f"query={query}"
        paging_response = await client.get(f"/api/gateway/integration/?{query_string}")

    assert paging_response.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir integration id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        integration_id = str(uuid4())
        response = await client.get(f"/api/gateway/integration/{integration_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_find_create_success(fixture):
    """Find metodunu test eder, varolan bir integration id olduğu için 200 dönmesi gerekiyor. """

    async with fixture.client() as client:
        create_gateway_api: CreateGatewayApi = generate_gateway_api()
        create_gateway_api_response = await client.post(
            "/api/gateway/gateway_api/",
            content=json.dumps([obj.model_dump(exclude_none=True)
                               for obj in [create_gateway_api]], cls=JsonEncoder)
        )
        assert create_gateway_api_response.status_code == 201
        gateway_api_id = create_gateway_api_response.json()["items"][0]["id"]

        create_connection_info: CreateConnectionInfo = CreateConnectionInfo(
            name="test_auth_info_test_app"+generate(size=4),
            description="test_auth_info_desc",
            params=generate_authorization_info().model_dump(),
            type=ConnectionInfoTypes.AUTHENTICATION
        )
        create_connection_infos = [create_connection_info]
        connection_info_content = json.dumps([obj.model_dump(
            exclude_none=True) for obj in create_connection_infos], cls=JsonEncoder)
        create_connection_info_response = await client.post(f"/api/gateway/connection_info/", content=connection_info_content)
        assert create_connection_info_response.status_code == 201
        connection_info_id = create_connection_info_response.json()[
            "items"][0]["id"]

        create_integration: CreateIntegration = generate_integration(
            gateway_api_id, connection_info_id)
        obj2 = [obj.model_dump(exclude_none=True) for obj in [create_integration]]
        obj2[0]["default_route"] = False
        obj2[0]["default_route_path"] = ""
        content2 = json.dumps(obj2, cls=JsonEncoder)
        create_integration_response = await client.post(
            "/api/gateway/integration/",
            content=content2)

    assert create_integration_response.status_code == 201
