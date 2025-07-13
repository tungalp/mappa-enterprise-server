import json
from random import random
import pytest

from mapa.core.data.query_args import Filter, FilterOp, QueryArgs


@pytest.mark.asyncio
async def test_adhoc_nodes_paging_query_param(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["openid"])
    async with fixture.client() as client:
        query_args = QueryArgs(
            limit=100,
            select=[
                "id",
                "name",
                # "parent_id"
            ],
            order={
                "name": "asc"
            },
            where=[
                Filter(field="id", op=FilterOp.IN, value=[11, 10, 3])
            ])
        endpoint = f"/admin/nodes/?query={query_args.model_dump_json()}"
        client.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        response = await client.get(endpoint)

    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert len(data["items"]) > 0
