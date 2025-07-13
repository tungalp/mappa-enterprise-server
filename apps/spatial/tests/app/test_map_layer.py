import json
from uuid import uuid4

import pytest
from mapa.core.data.json_encoder import JsonEncoder
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.spatial.connection.connection_model import CreateConnection
from mapa.spatial.layer.layer_model import CreateLayer
from mapa.spatial.map.map_model import CreateMap
from mapa.spatial.map_layer.map_layer_model import CreateMapLayer
from mapa.spatial.namespace.namespace_model import CreateNamespace

from .data import (generate_connection, generate_layer, generate_map,
                   generate_map_layer, generate_namespace)


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
        paging_response = await client.get(f"/api/spatial/map_layer/?{query_string}")

    assert paging_response.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir layer id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        map_layer_id = str(uuid4())
        response = await client.get(f"/api/spatial/map_layer/{map_layer_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_find_create_success(fixture):
    """Create metodunu test eder, varolan bir layer id olduğu için 200 dönmesi gerekiyor. """

    async with fixture.client() as client:
        create_connection: CreateConnection = generate_connection()
        create_connection_response = await client.post(
            "/api/spatial/connection/",
            content=json.dumps([obj.model_dump(exclude_none=True)
                               for obj in [create_connection]], cls=JsonEncoder)
        )
        assert create_connection_response.status_code == 201

        create_layer: CreateLayer = generate_layer(
            create_connection_response.json()["items"][0]["id"])
        create_layer_response = await client.post(
            "/api/spatial/layer/",
            content=json.dumps([obj.model_dump(exclude_none=True)
                               for obj in [create_layer]], cls=JsonEncoder)
        )
        assert create_layer_response.status_code == 201

        layer_def_query_args: QueryArgs = QueryArgs(where=[
            Filter(field="layer_id", op=FilterOp.EQUAL,
                   value=create_layer_response.json()["items"][0]["id"]),
        ],
            order={
            "id": "desc"
        })
        layer_def_query = layer_def_query_args.model_dump_json()
        layer_def_query_string = f"query={layer_def_query}"
        layer_def_paging_response = await client.get(f"/api/spatial/layer_definition/?{layer_def_query_string}")
        assert layer_def_paging_response.status_code == 200

        create_namespace: CreateNamespace = generate_namespace()
        create_namespace_response = await client.post(
            "/api/spatial/namespace/",
            content=json.dumps([obj.model_dump(exclude_none=True)
                               for obj in [create_namespace]], cls=JsonEncoder)
        )
        assert create_namespace_response.status_code == 201

        create_map: CreateMap = generate_map(
            create_namespace_response.json()["items"][0]["id"])
        create_map_response = await client.post(
            "/api/spatial/map/",
            content=json.dumps([obj.model_dump(exclude_none=True)
                               for obj in [create_map]], cls=JsonEncoder)
        )
        assert create_map_response.status_code == 201

        create_map_layer: CreateMapLayer = generate_map_layer(
            create_map_response.json()["items"][0]["id"], layer_def_paging_response.json()["items"][0]["id"])

        create_map_layer_response = await client.post(
            "/api/spatial/map_layer/",
            content=json.dumps([obj.model_dump(exclude_none=True)
                               for obj in [create_map_layer]], cls=JsonEncoder)
        )
        assert create_map_layer_response.status_code == 201

        map_layer_id = create_map_layer_response.json()["items"][0]["id"]
        field_list = ["id", "name", "parent_id", "params",
                      "order", "map_id", "layer_definition_id"]
        response = await client.get(f'/api/spatial/map_layer/{map_layer_id}?field_list={json.dumps(field_list)}')
    assert response.status_code == 200