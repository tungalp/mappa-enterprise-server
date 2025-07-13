import json
from typing import List
from uuid import uuid4

import pytest
from mapa.core.data.json_encoder import JsonEncoder
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.spatial.reference.reference_model import CreateReference

from .data import generate_reference


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
        paging_response = await client.get(f"/api/spatial/reference/?{query_string}")

    assert paging_response.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir reference id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        reference_id = str(uuid4())
        response = await client.get(f"/api/spatial/reference/{reference_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_find_create_success(fixture):
    """Create metodunu test eder, varolan bir reference id olduğu için 200 dönmesi gerekiyor. """

    async with fixture.client() as client:
        create_reference: List[CreateReference] = generate_reference()
        create_reference_response = await client.post(
            "/api/spatial/reference/",
            content=json.dumps([obj.model_dump(exclude_none=True)
                               for obj in [create_reference[0]]], cls=JsonEncoder)
        )
        assert create_reference_response.status_code == 201
        reference_id = create_reference_response.json()["items"][0]["id"]
        field_list = ["id", "epsgcode", "wkid", "wkt","projcs","name"]
        response = await client.get(f'/api/spatial/reference/{reference_id}?field_list={json.dumps(field_list)}')

    assert response.status_code == 200