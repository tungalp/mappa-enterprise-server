import json
from uuid import uuid4
from mapa.core.data.json_encoder import JsonEncoder
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.gateway.gateway_api.gateway_api_model import CreateGatewayApi
from .data import generate_gateway_api, generate_route
from mapa.gateway.route.route_model import CreateRoute
import pytest


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
        paging_response = await client.get(f"/api/gateway/route/?{query_string}")

    assert paging_response.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir route id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        route_id = str(uuid4())
        response = await client.get(f"/api/gateway/route/{route_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_find_create_success(fixture):
    """Find metodunu test eder, varolan bir route id olduğu için 200 dönmesi gerekiyor. """

    async with fixture.client() as client:
        
        create_gateway_api: CreateGatewayApi = generate_gateway_api()
        create_gateway_api_response = await client.post(
            "/api/gateway/gateway_api/",
            content=json.dumps([obj.model_dump(exclude_none=True) for obj in [create_gateway_api]], cls=JsonEncoder)
        )
        assert create_gateway_api_response.status_code == 201
        gateway_api_id = create_gateway_api_response.json()["items"][0]["id"]
        
        create_route: CreateRoute = generate_route(gateway_api_id)
        create_route_response = await client.post(
            "/api/gateway/route/",
            content=json.dumps([obj.model_dump(exclude_none=True) for obj in [create_route]], cls=JsonEncoder))

    assert create_route_response.status_code == 201
