from uuid import uuid4
from mapa.core.data.json_encoder import JsonEncoder
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from .conftest import generate_api
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
        pagingresponse = await client.get(f"/api/manage/api/?{query_string}")

    assert pagingresponse.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir api id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        api_id = str(uuid4())
        response = await client.get(f"/api/manage/api/{api_id}")

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
