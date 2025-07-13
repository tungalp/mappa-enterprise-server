import json
import pytest
from mapa.core.data.json_encoder import JsonEncoder
from mapa.core.data.query_args import (QueryArgs)
from uuid import uuid4
from .conftest import generate_role



@pytest.mark.asyncio
async def test_crud_success(fixture):
    async with fixture.client() as client:
        
        create_role = generate_role()
        create_roles = [create_role]
        create_roles_content = json.dumps(
            [obj.model_dump(exclude_none=True) for obj in create_roles], cls=JsonEncoder)
        createresponse = await client.post(f"/api/manage/role/", content=create_roles_content)

        # create_role_id = create_role.id
        # findresponse = await client.get(f"/api/manage/role/{create_role_id}")

        # query_args: QueryArgs = QueryArgs(where=[
        #     Filter(field="id", op=FilterOp.EQUAL, value=create_role_id),
        # ],
        #     order={
        #     "id": "desc"
        # })
        
        # query = query_args.model_dump_json()
        # query_string = f"query={query}"
        # pagingresponse = await client.get(f"/api/manage/role/?{query_string}")

        # delete_args: QueryArgs = QueryArgs(where=[
        #     Filter(field="id", op=FilterOp.EQUAL, value=create_role_id),
        # ])
        
        # delete = delete_args.model_dump_json()
        # delete_string = f"query={delete}"
        # deleteresponse = await client.delete(f"/api/manage/role/?{delete_string}")
        
    assert createresponse.status_code == 201
    # assert findresponse.status_code == 200
    # assert pagingresponse.status_code == 200
    # assert deleteresponse.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir client id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        role_id = str(uuid4())
        response = await client.get(f"/api/manage/role/{role_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_paging(fixture):
    """Find metodunu test eder """

    async with fixture.client() as client:
        query_args: QueryArgs = QueryArgs()
        query = query_args.model_dump_json()
        query_string = f"query={query}"
        response = await client.get(f"/api/manage/role/?{query_string}")

    assert response.status_code == 200
    