from uuid import uuid4
import uuid
from mapa.core.data.json_encoder import JsonEncoder
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from .conftest import generate_api_scope, generate_api
from mapa.manage.api_scope.api_scope_model import CreateApiScope
import pytest
import json


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
        pagingresponse = await client.get(f"/api/manage/api_scope/?{query_string}")

    assert pagingresponse.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir api id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        id = str(uuid4())
        response = await client.get(f'/api/manage/api_scope/{id}')

    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_success(fixture):
    """Find metodunu test eder, varolan bir api id olduğu için 200 dönmesi gerekiyor. """

    async with fixture.client() as client:
        create_api = generate_api()
        create_apis = [create_api]
        apis_content=json.dumps([obj.model_dump(exclude_none=True) for obj in create_apis],cls=JsonEncoder)
        createapiresponse = await client.post(f"/api/manage/api/", content=apis_content)
        assert createapiresponse.status_code == 201

        query_args: QueryArgs = QueryArgs(where=[
            Filter(field="name", op=FilterOp.EQUAL, value=create_api.name),
        ])
        query = query_args.model_dump_json()
        query_string = f"query={query}"
        pagingresponse = await client.get(f"/api/manage/api/?{query_string}")

        pagresult = pagingresponse.json()
        api_id = uuid.UUID(pagresult['items'][0]['id'])
        create_api_scope: CreateApiScope = generate_api_scope(api_id)
        create_api_scopes = [create_api_scope]
        create_api_scopes_content=json.dumps([obj.model_dump(exclude_none=True) for obj in create_api_scopes],cls=JsonEncoder)
        createresponse = await client.post(f"/api/manage/api_scope/", content=create_api_scopes_content)

    assert createresponse.status_code == 201
