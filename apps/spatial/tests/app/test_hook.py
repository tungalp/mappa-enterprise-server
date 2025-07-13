from uuid import uuid4

import pytest
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs


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
        paging_response = await client.get(f"/api/spatial/hook/?{query_string}")

    assert paging_response.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir hook id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        hook_id = str(uuid4())
        response = await client.get(f"/api/spatial/hook/{hook_id}")

    assert response.status_code == 404

# Ekleme işlemi olmayacağı için test edilip kapatılmıştır
# @pytest.mark.asyncio
# async def test_find_create_success(fixture):
#     """Create metodunu test eder, varolan bir hook id olduğu için 200 dönmesi gerekiyor. """

#     async with fixture.client() as client:
#         create_hooks: List[CreateHook] = generate_hook_list()
#         create_hook_response = await client.post(
#             "/api/spatial/hook/",
#             content=json.dumps([obj.model_dump(exclude_none=True)
#                                for obj in create_hooks], cls=JsonEncoder)
#         )
#         assert create_hook_response.status_code == 201

#         hook_id = create_hook_response.json()["items"][0]["id"]
#         field_list = ["id", "type", "operation_type", "description"]
#         response = await client.get(f'/api/spatial/hook/{hook_id}?field_list={json.dumps(field_list)}')

#         assert response.status_code == 200
