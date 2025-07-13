import json
from uuid import uuid4

import pytest
from mapa.core.data.json_encoder import JsonEncoder
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.spatial.definition.definition_model import CreateDefinition

from .data import generate_definition


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
        paging_response = await client.get(f"/api/spatial/definition/?{query_string}")

    assert paging_response.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir definition id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        definition_id = str(uuid4())
        response = await client.get(f"/api/spatial/definition/{definition_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_find_create_success(fixture):
    """Create metodunu test eder, varolan bir definition id olduğu için 200 dönmesi gerekiyor. """
    
    async with fixture.client() as client:
        create_definition: CreateDefinition = generate_definition()
        create_definition_response = await client.post(
            "/api/spatial/definition/",
            content=json.dumps([obj.model_dump(exclude_none=True)
                                for obj in [create_definition]], cls=JsonEncoder)
        ) 
        assert create_definition_response.status_code == 201
        definition_id = create_definition_response.json()["items"][0]["id"]
        field_list = ["id", "title", "default_extent", "max_scale", "min_scale","opacity", "timer", "is_attribute_panel","organization_geo_constraint", "is_base_layer", "edit_snap_scale","field_params", "data_type","key_field","target_namespace","type_name","style_params", "topology_rules_params", "filter_params"]
        response = await client.get(f'/api/spatial/definition/{definition_id}?field_list={json.dumps(field_list)}')
    assert response.status_code == 200