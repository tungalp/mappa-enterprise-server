import json
import pytest
from uuid import uuid4

from mapa.core.data.json_encoder import JsonEncoder
from .conftest import generate_user
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs


@pytest.mark.asyncio
async def test_crud_success(fixture):

    async with fixture.client() as client:
        create_user = generate_user()
        create_users = [create_user]
        content = json.dumps([obj.model_dump(exclude_none=True)
                             for obj in create_users], cls=JsonEncoder)

        # createresponse = await client.post(f"/api/manage/user/", content=json.dumps([obj.dict for obj in create_users]))
        # createresponse = await client.post(f"/api/manage/user/", content=json.dumps(create_users))
        # createresponse = await client.post(f"/api/manage/user/", content=[create_users[0].json(exclude_none=True)])
        createresponse = await client.post(f"/api/manage/user/", content=content)

        # create_user_id = create_user.id
        # findresponse = await client.get(f"/api/manage/user/{create_user_id}")
        create_user.name = "service user"
        query_args: QueryArgs = QueryArgs(where=[
            Filter(field="name", op=FilterOp.EQUAL, value=create_user.name),
        ])

        query = query_args.model_dump_json()
        query_string = f"query={query}"
        pagingresponse = await client.get(f"/api/manage/user/?{query_string}")

        delete_args: QueryArgs = QueryArgs(where=[
            Filter(field="id", op=FilterOp.EQUAL, value=str(uuid4())),
        ])

        delete = delete_args.model_dump_json()
        delete_string = f"query={delete}"
        deleteresponse = await client.delete(f"/api/manage/user/?{delete_string}")

    assert createresponse.status_code == 201
    assert pagingresponse.status_code == 200
    assert deleteresponse.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir user id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        user_id = str(uuid4())
        response = await client.get(f"/api/manage/user/{user_id}")

    assert response.status_code == 404


    
    
@pytest.mark.asyncio
async def test_user_organization_role_api_scopes(fixture):
    """Find metodunu test eder """

    async with fixture.client() as client:
        query_args: QueryArgs = QueryArgs(
            where=[
                Filter(field="id", op=FilterOp.EQUAL, value=str("2ac6175d-4843-4c3f-a1c6-41ef3f515a2c")),
                ],
            select=["id", "name", "surname", "email", "password", "email_verified", "phone", "context", "subject_id", "created_at",
                    "organizations.name","organizations.description","organizations.parent_id","organizations.is_root","organizations.integration_id","organizations.organization_type_id","organizations.is_hierarchical",
                    "organizations.roles.id","organizations.roles.name","organizations.roles.description",
                    "organizations.roles.api_scopes.name","organizations.roles.api_scopes.description","organizations.roles.api_scopes.api_id"
                ],
            limit=0,
            offset=0
            )
        query = query_args.model_dump_json()
        query_string = f"query={query}"
        paging_response = await client.get(f"/api/manage/user/?{query_string}")

    assert paging_response.status_code == 200