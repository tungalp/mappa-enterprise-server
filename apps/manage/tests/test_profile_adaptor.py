import json
import pytest
from mapa.core.data.json_encoder import JsonEncoder
from mapa.core.data.query_args import (
    Filter, FilterOp, QueryArgs)
from uuid import uuid4
from .conftest import generate_profile_adaptor

@pytest.mark.asyncio
async def test_crud_success(fixture):

    async with fixture.client() as client:
        create_profile_adaptor = generate_profile_adaptor()
        create_profile_adaptors = [create_profile_adaptor]
        create_profile_adaptor_content = json.dumps(
            [obj.model_dump(exclude_none=True) for obj in create_profile_adaptors], cls=JsonEncoder)

        createresponse = await client.post(f"/api/manage/profile_adaptor/", content=create_profile_adaptor_content)

        create_profile_adaptor_id = createresponse.json()['items'][0]['id']
        findresponse = await client.get(f"/api/manage/profile_adaptor/{create_profile_adaptor_id}")

        query_args: QueryArgs = QueryArgs(where=[
            Filter(field="id", op=FilterOp.EQUAL,
                   value=create_profile_adaptor_id),
        ])

        query = query_args.model_dump_json()
        query_string = f"query={query}"
        pagingresponse = await client.get(f"/api/manage/profile_adaptor/?{query_string}")

        delete_args: QueryArgs = QueryArgs(where=[
            Filter(field="id", op=FilterOp.EQUAL,
                   value=create_profile_adaptor_id),
        ])

        delete = delete_args.model_dump_json()
        delete_string = f"query={delete}"
        deleteresponse = await client.delete(f"/api/manage/profile_adaptor/?{delete_string}")

    assert createresponse.status_code == 201
    assert findresponse.status_code == 200
    assert pagingresponse.status_code == 200
    assert deleteresponse.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir profile adaptor id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        profile_adaptor_id = str(uuid4())
        response = await client.get(f"/api/manage/profile_adaptor/{profile_adaptor_id}")

    assert response.status_code == 404
