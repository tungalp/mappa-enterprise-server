import json
from uuid import uuid4

import pytest
from mapa.core.data.json_encoder import JsonEncoder
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.organization_type.organization_type_model import CreateOrganizationType

from .data import generate_organization_type


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
        paging_response = await client.get(f"/api/manage/organization_type/?{query_string}")

    assert paging_response.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir organization_type id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        id = str(uuid4())
        response = await client.get(f"/api/manage/organization_type/{id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_find_create_success(fixture):
    """Create metodunu test eder, varolan bir organization_type id olduğu için 200 dönmesi gerekiyor. """

    async with fixture.client() as client:
        create_organization_type: CreateOrganizationType = generate_organization_type()
        create_organization_type_response = await client.post(
            "/api/manage/organization_type/",
            content=json.dumps([obj.model_dump(exclude_none=True)
                               for obj in [create_organization_type]], cls=JsonEncoder)
        )
        assert create_organization_type_response.status_code == 201
        base_layer_id = create_organization_type_response.json()["items"][0]["id"]
        field_list = ["id", "name", "description","is_root","parent_id"]
        response = await client.get(f'/api/manage/organization_type/{base_layer_id}?field_list={json.dumps(field_list)}')
    assert response.status_code == 200