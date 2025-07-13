import json
from uuid import uuid4
from nanoid import generate
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.core.data.json_encoder import JsonEncoder
from mapa.gateway.connection_info.authentication_info_model import CreateAuthenticationInfo
from mapa.gateway.connection_info.connection_info_model import CreateConnectionInfo
from mapa.gateway.constant import ConnectionInfoTypes
from .data import generate_authorization_info, generate_connection_info
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
        paging_response = await client.get(f"/api/gateway/connection_info/?{query_string}")

    assert paging_response.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir connection_info id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        connection_info_id = str(uuid4())
        response = await client.get(f"/api/gateway/connection_info/{connection_info_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_find_create_success(fixture):
    """Find metodunu test eder, varolan bir connection_info id olduğu için 200 dönmesi gerekiyor. """

    async with fixture.client() as client:
        create_connection_info: CreateConnectionInfo = generate_connection_info()
        create_connection_info_response = await client.post(
            "/api/gateway/connection_info/",
            content=json.dumps([obj.model_dump(exclude_none=True) for obj in [create_connection_info]], cls=JsonEncoder)
        )
    assert create_connection_info_response.status_code == 201