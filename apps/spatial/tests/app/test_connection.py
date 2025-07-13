import json
from uuid import uuid4

import pytest
from mapa.core.data.json_encoder import JsonEncoder
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.spatial.connection.connection_model import CreateConnection

from .data import generate_connection


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
        paging_response = await client.get(f"/api/spatial/connection/?{query_string}")

    assert paging_response.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir connection id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        connection_id = str(uuid4())
        response = await client.get(f"/api/spatial/connection/{connection_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_find_create_success(fixture):
    """Create metodunu test eder, varolan bir connection id olduğu için 200 dönmesi gerekiyor. """

    async with fixture.client() as client:
        create_connection: CreateConnection = generate_connection()
        create_connection_response = await client.post(
            "/api/spatial/connection/",
            content=json.dumps([obj.model_dump(exclude_none=True)
                               for obj in [create_connection]], cls=JsonEncoder)
        )
        assert create_connection_response.status_code == 201
        connection_id = create_connection_response.json()["items"][0]["id"]
        field_list = ["id", "name", "description", "route_params","type"]
        response = await client.get(f'/api/spatial/connection/{connection_id}?field_list={json.dumps(field_list)}')

    assert response.status_code == 200