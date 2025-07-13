import json
from uuid import uuid4
from mapa.core.data.json_encoder import JsonEncoder
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from .data import generate_gateway_api
from mapa.gateway.gateway_api.gateway_api_model import CreateGatewayApi
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
        paging_response = await client.get(f"/api/gateway/gateway_api/?{query_string}")

    assert paging_response.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir api id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        gateway_api_id = str(uuid4())
        response = await client.get(f"/api/gateway/gateway_api/{gateway_api_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_find_create_success(fixture):
    """Create metodunu test eder, varolan bir api id olduğu için 200 dönmesi gerekiyor. """

    async with fixture.client() as client:
        create_gateway_api: CreateGatewayApi = generate_gateway_api()
        create_gateway_api_response = await client.post(
            "/api/gateway/gateway_api/",
            content=json.dumps([obj.model_dump(exclude_none=True) for obj in [create_gateway_api]], cls=JsonEncoder)
        )
    assert create_gateway_api_response.status_code == 201


async def test_get(fixture):
    """Find metodunu test eder, olmayan bir api id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        create_gateway_api: CreateGatewayApi = generate_gateway_api()
        create_gateway_api_response = await client.post(
            "/api/gateway/gateway_api/",
            content=json.dumps([obj.model_dump(exclude_none=True) for obj in [create_gateway_api]], cls=JsonEncoder)
        )
        assert create_gateway_api_response.status_code == 201
        gateway_api_id = create_gateway_api_response.json()["items"][0]["id"]
        field_list = ["id", "name", "type", "path", "identifier", "context"]
        response = await client.get(f'/api/gateway/gateway_api/{gateway_api_id}?field_list={json.dumps(field_list)}')
        
    assert response.status_code == 200

    # assert response.status_code == 404

# @pytest.mark.asyncio
# async def test_create_all_success(fixture):
#     """Find metodunu test eder, varolan bir api id olduğu için 200 dönmesi gerekiyor. """

#     async with fixture.client() as client:
#         create_api = generate_api()
#         create_apis = [create_api]
#         createapiresponse = await client.post(f"/api/gateway/gateway_api/", content=json.dumps([obj.__dict__ for obj in create_apis]))

#     assert createapiresponse.status_code == 200
