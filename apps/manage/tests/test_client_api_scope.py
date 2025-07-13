import json
from uuid import uuid4
from mapa.core.data.json_encoder import JsonEncoder
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from .conftest import generate_api_scope, generate_api, generate_client, generate_client_api_scope, generate_client_api
from mapa.manage.api.api_model import CreateApi
from mapa.manage.api_scope.api_scope_model import CreateApiScope
import pytest


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
        pagingresponse = await client.get(f"/api/manage/client_api_scope/?{query_string}")

    assert pagingresponse.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir api id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        id = str(uuid4())
        response = await client.get(f"/api/manage/client_api_scope/{id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_success(fixture):
    """Find metodunu test eder, varolan bir api id olduğu için 200 dönmesi gerekiyor. """

    async with fixture.client() as client:

        create_client = generate_client()
        create_clients = [create_client]
        clients_content = json.dumps(
            [obj.model_dump(exclude_none=True) for obj in create_clients], cls=JsonEncoder)

        createclientresponse = await client.post(f"/api/manage/client/", content=clients_content)
        assert createclientresponse.status_code == 201

        create_api: CreateApi = generate_api()
        create_apis = [create_api]
        apis_content = json.dumps([obj.model_dump(exclude_none=True)
                             for obj in create_apis], cls=JsonEncoder)

        createapiresponse = await client.post(f"/api/manage/api/", content=apis_content)
        assert createapiresponse.status_code == 201

        api_id = createapiresponse.json()['items'][0]['id']
        client_id = createclientresponse.json()['items'][0]['id']

        client_api = generate_client_api(client_id, api_id)
        client_apis = [client_api]
        client_apis_content = json.dumps([obj.model_dump(exclude_none=True)
                             for obj in client_apis], cls=JsonEncoder)
        creatclientapiresponse = await client.post(f"/api/manage/client_api/", content=client_apis_content)
        assert creatclientapiresponse.status_code == 201

        client_api_id = creatclientapiresponse.json()['items'][0]['id']

        query_args: QueryArgs = QueryArgs(where=[
            Filter(field="id", op=FilterOp.EQUAL, value=api_id),
        ])
        query=query_args.model_dump_json()
        query_string=f"query={query}"
        pagingresponse=await client.get(f"/api/manage/api/?{query_string}")

        api_id=pagingresponse.json()['items'][0]['id']
        create_api_scope: CreateApiScope=generate_api_scope(api_id)
        create_api_scopes = [create_api_scope]
        create_api_scopes_content = json.dumps([obj.model_dump(exclude_none=True)
                             for obj in create_api_scopes], cls=JsonEncoder)
        createapiscoperesponse=await client.post(f"/api/manage/api_scope/", content = create_api_scopes_content)
        assert createapiscoperesponse.status_code == 201

        query_args: QueryArgs=QueryArgs(where = [
            Filter(field="name", op=FilterOp.EQUAL,
                   value=create_api_scope.name),
        ])
        query=query_args.model_dump_json()
        query_string=f"query={query}"
        apiscopepagingresponse=await client.get(f"/api/manage/api_scope/?{query_string}")
        api_scope_id=apiscopepagingresponse.json()['items'][0]['id']

        query_args: QueryArgs=QueryArgs(where = [
            Filter(field="id", op=FilterOp.EQUAL,
                   value=client_id),
        ])
        query=query_args.model_dump_json()
        query_string=f"query={query}"
        clientpagingresponse=await client.get(f"/api/manage/client/?{query_string}")
        client_id=clientpagingresponse.json()['items'][0]['id']

        client_api_scope=generate_client_api_scope(client_api_id, api_scope_id)
        client_api_scopes= [client_api_scope]
        client_api_scopes_content = json.dumps([obj.model_dump(exclude_none=True)
                             for obj in client_api_scopes], cls=JsonEncoder)
        creatclientapiscoperesponse=await client.post(f"/api/manage/client_api_scope/", content = client_api_scopes_content)

    assert creatclientapiscoperesponse.status_code == 201
