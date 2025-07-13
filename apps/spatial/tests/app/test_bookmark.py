from uuid import uuid4

import pytest
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs


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
        paging_response = await client.get(f"/api/spatial/bookmark/?{query_string}")

    assert paging_response.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir bookmark id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        bookmark_id = str(uuid4())
        response = await client.get(f"/api/spatial/bookmark/{bookmark_id}")

    assert response.status_code == 404
