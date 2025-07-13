import json
from typing import Any, Dict
from mapa.core.data.json_encoder import JsonEncoder
from mapa.core.data.query_args import QueryArgs
import pytest

from mapa.gateway.context_var.context_var_model import CreateConvextVar
from .data import generate_context_var

@pytest.mark.asyncio
async def test_paging(fixture):
    """Find metodunu test eder """

    async with fixture.client() as client:
        query_args: QueryArgs = QueryArgs(
            order={
                "id": "desc"
            }
        )
        query = query_args.model_dump_json()
        query_string = f"query={query}"
        paging_response = await client.get(f"/api/gateway/context_var/?{query_string}")

    assert paging_response.status_code == 200
    data = paging_response.json()["items"]
    assert len(data) > 0


@pytest.mark.asyncio
async def test_find_create_find_delete_success(fixture):
    """Create metodunu test eder. """

    async with fixture.client() as client:
        # create context variable
        create_context_var: CreateConvextVar = generate_context_var()
        create_context_var_content = json.dumps(
            [obj.model_dump(exclude_none=True) for obj in [create_context_var]], cls=JsonEncoder)
        create_response = await client.post(f"/api/gateway/context_var/", content=create_context_var_content)
        assert create_response.status_code == 201
        
        # find context variable
        data: Dict[str, Any] = create_response.json()
        assert data is not None
        
        item_response = await client.get(f"/api/gateway/context_var/{data['items'][0]['id']}")
    assert item_response is not None
        

