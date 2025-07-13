import json
import pytest
from mapa.core.data.json_encoder import JsonEncoder
from mapa.core.data.query_args import (Filter, FilterOp, QueryArgs)
from uuid import uuid4
from .conftest import generate_api, generate_api_scope, generate_role, generate_role_api_scope

@pytest.mark.asyncio
async def test_crud_success(fixture):

    async with fixture.client() as client:       
        create_api = generate_api()
        create_apis = [create_api]
        apis_content = json.dumps([obj.model_dump(exclude_none=True)
                                  for obj in create_apis], cls=JsonEncoder)
        create_api_response = await client.post(f"/api/manage/api/", content=apis_content)
        assert create_api_response.status_code == 201
        api_id = create_api_response.json()['items'][0]['id']

        create_api_scope = generate_api_scope(api_id)
        create_api_scopes = [create_api_scope]
        create_api_scopes_content = json.dumps(
            [obj.model_dump(exclude_none=True) for obj in create_api_scopes], cls=JsonEncoder)
        create_api_scope_response = await client.post(f"/api/manage/api_scope/", content=create_api_scopes_content)
        assert create_api_scope_response.status_code == 201
        api_scope_id = create_api_scope_response.json()['items'][0]['id']
        
        create_role = generate_role()
        create_roles = [create_role]
        create_roles_content = json.dumps(
            [obj.model_dump(exclude_none=True) for obj in create_roles], cls=JsonEncoder)
        create_role_response = await client.post(f"/api/manage/role/", content=create_roles_content)
        assert create_role_response.status_code == 201
        role_id = create_role_response.json()['items'][0]['id']
        
        create_role_api_scope = generate_role_api_scope(role_id, api_scope_id)
        create_role_api_scopes = [create_role_api_scope]
        create_role_api_scope_content = json.dumps(
            [obj.model_dump(exclude_none=True) for obj in create_role_api_scopes], cls=JsonEncoder)

        create_role_api_scope_response = await client.post(f"/api/manage/role_api_scope/", content=create_role_api_scope_content)

        create_role_api_scope_id = create_role_api_scope_response.json()['items'][0]['id']
        findresponse = await client.get(f"/api/manage/role_api_scope/{create_role_api_scope_id}")

        query_args: QueryArgs = QueryArgs(where=[
            Filter(field="id", op=FilterOp.EQUAL, value=create_role_api_scope_id),
        ])
        
        query = query_args.model_dump_json()
        query_string = f"query={query}"
        pagingresponse = await client.get(f"/api/manage/role_api_scope/?{query_string}")

        delete_args: QueryArgs = QueryArgs(where=[
            Filter(field="id", op=FilterOp.EQUAL, value=create_role_api_scope_id),
        ])
        
        delete = delete_args.model_dump_json()
        delete_string = f"query={delete}"
        deleteresponse = await client.delete(f"/api/manage/role_api_scope/?{delete_string}")
        
    assert create_role_api_scope_response.status_code == 201
    assert findresponse.status_code == 200
    assert pagingresponse.status_code == 200
    assert deleteresponse.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir role_api_scope api scope id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        role_api_scope_id = str(uuid4())
        response = await client.get(f"/api/manage/role_api_scope/{role_api_scope_id}")

    assert response.status_code == 404