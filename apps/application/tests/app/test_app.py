from uuid import uuid4
from mapa.core.data.json_encoder import JsonEncoder
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from ..data import generate_app
import pytest
import json

@pytest.mark.asyncio
async def test_paging(fixture):
    """Find metodunu test eder """
    async with fixture.client() as client:
        query_args: QueryArgs = QueryArgs(where=[
            Filter(field="id", op=FilterOp.EQUAL, value=str(uuid4())),
        ])
        query = query_args.model_dump_json()
        query_string = f"query={query}"
        paging_response = await client.get(f"/api/application/app/?{query_string}")

    assert paging_response.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir api id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        api_id = str(uuid4())
        response = await client.get(f"/api/application/app/{api_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_success(fixture):
    """Find metodunu test eder, varolan bir api id olduğu için 200 dönmesi gerekiyor. """

    async with fixture.client() as client:
        create_app = generate_app()
        create_apps = [create_app]
        create_apps_content = json.dumps([obj.model_dump(exclude_none=True) for obj in create_apps], cls=JsonEncoder)

        create_response = await client.post(f"/api/application/app/", content=create_apps_content)
        
    assert create_response.status_code == 201


# @pytest.mark.asyncio
# async def test_create_all_success(fixture):
#     """Find metodunu test eder, varolan bir api id olduğu için 200 dönmesi gerekiyor. """

#     async with fixture.client() as client:
#         create_app = generate_app()
#         create_apps = [create_app]
#         response = await client.post(f"/api/application/app/", content=json.dumps([obj.__dict__ for obj in create_apps]))

#     assert response.status_code == 200
