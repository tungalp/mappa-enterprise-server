import json
from uuid import uuid4

import pytest
from mapa.core.data.json_encoder import JsonEncoder
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.spatial.base_layer.base_layer_model import CreateBaseLayer
from mapa.spatial.map.map_model import CreateMap
from mapa.spatial.map_base_layer.map_base_layer_model import CreateMapBaseLayer
from mapa.spatial.namespace.namespace_model import CreateNamespace

from .data import (generate_base_layer, generate_map, generate_map_base_layer,
                   generate_namespace)


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
        paging_response = await client.get(f"/api/spatial/map_base_layer/?{query_string}")

    assert paging_response.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir map_base_layer id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        map_base_layer_id = str(uuid4())
        response = await client.get(f"/api/spatial/map_base_layer/{map_base_layer_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_find_create_success(fixture):
    """Create metodunu test eder, varolan bir map_base_layer id olduğu için 200 dönmesi gerekiyor. """

    async with fixture.client() as client:

        create_namespace: CreateNamespace = generate_namespace()
        create_namespace_response = await client.post(
            "/api/spatial/namespace/",
            content=json.dumps([obj.model_dump(exclude_none=True)
                               for obj in [create_namespace]], cls=JsonEncoder)
        )

        create_map: CreateMap = generate_map(
            create_namespace_response.json()["items"][0]["id"])
        create_map_response = await client.post(
            "/api/spatial/map/",
            content=json.dumps([obj.model_dump(exclude_none=True)
                               for obj in [create_map]], cls=JsonEncoder)
        )

        create_base_layer: CreateBaseLayer = generate_base_layer()
        create_base_layer_response = await client.post(
            "/api/spatial/base_layer/",
            content=json.dumps([obj.model_dump(exclude_none=True)
                               for obj in [create_base_layer]], cls=JsonEncoder)
        )

        create_map_base_layer: CreateMapBaseLayer = generate_map_base_layer(create_map_response.json()["items"][0]["id"],
                                                                            create_base_layer_response.json()["items"][0]["id"])
        create_map_base_layer_response = await client.post(
            "/api/spatial/map_base_layer/",
            content=json.dumps([obj.model_dump(exclude_none=True)
                               for obj in [create_map_base_layer]], cls=JsonEncoder)
        )
        assert create_map_base_layer_response.status_code == 201
        map_base_layer_id = create_map_base_layer_response.json()[
            "items"][0]["id"]
        field_list = ["id", "map_id", "base_layer_id", "order"]
        response = await client.get(f'/api/spatial/map_base_layer/{map_base_layer_id}?field_list={json.dumps(field_list)}')

    assert response.status_code == 200