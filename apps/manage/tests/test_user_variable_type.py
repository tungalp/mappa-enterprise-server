import json
from uuid import uuid4
import pytest
from mapa.core.data.json_encoder import JsonEncoder
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.manage.user_variable_type.user_variable_type_model import CreateUserVariableType
from .data import generate_user_variable_type

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
        paging_response = await client.get(f"/api/manage/user_variable_type/?{query_string}")

    assert paging_response.status_code == 200


@pytest.mark.asyncio
async def test_find_error(fixture):
    """Find metodunu test eder, olmayan bir user_variable_type id olduğu için 404 dönmesi gerekiyor. """

    async with fixture.client() as client:
        id = str(uuid4())
        response = await client.get(f"/api/manage/user_variable_type/{id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_find_create_success(fixture):
    """Create metodunu test eder, varolan bir user_variable_type id olduğu için 200 dönmesi gerekiyor. """

    async with fixture.client() as client:
      
        create_user_variable_type: CreateUserVariableType = generate_user_variable_type("test_name","test_desc")
        create_user_variable_type_response = await client.post(
            "/api/manage/user_variable_type/",
            content=json.dumps([obj.model_dump(exclude_none=True)
                               for obj in [create_user_variable_type]], cls=JsonEncoder)
        )
        assert create_user_variable_type_response.status_code == 201
        base_layer_id = create_user_variable_type_response.json()["items"][0]["id"]
        field_list = ["id", "name", "description"]
        response = await client.get(f'/api/manage/user_variable_type/{base_layer_id}?field_list={json.dumps(field_list)}')
        
    assert response.status_code == 200
    
