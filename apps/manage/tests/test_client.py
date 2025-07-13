import json
from uuid import uuid4
from mapa.core.data.json_encoder import JsonEncoder
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from .conftest import generate_client
import pytest


@pytest.mark.asyncio
async def test_paging(fixture):
    """Find metodunu test eder """

    async with fixture.client() as client:
        query_args: QueryArgs = QueryArgs()
        query = query_args.model_dump_json()
        query_string = f"query={query}"
        pagingresponse = await client.get(f"/api/manage/client/?{query_string}")

    assert pagingresponse.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir client id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        client_id = str(uuid4())
        response = await client.get(f"/api/manage/client/{client_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_success(fixture):
    """Find metodunu test eder, varolan bir client id olduğu için 200 dönmesi gerekiyor. """

    async with fixture.client() as client:
        create_client = generate_client()
        create_clients = [create_client]
        clients_content = json.dumps(
            [obj.model_dump(exclude_none=True) for obj in create_clients], cls=JsonEncoder)

        create_response = await client.post(f"/api/manage/client/", content=clients_content)

        client_id = create_response.json()['items'][0]['client_id']
        findresponse = await client.get(f"/api/manage/client/info/{client_id}")

        query_args: QueryArgs = QueryArgs(where=[
            Filter(field="client_id", op=FilterOp.EQUAL, value=client_id),
        ])
        query = query_args.model_dump_json()
        query_string = f"query={query}"
        pagingresponse = await client.get(f"/api/manage/client/?{query_string}")

    assert create_response.status_code == 201
    assert findresponse.status_code == 200
    assert pagingresponse.status_code == 200
