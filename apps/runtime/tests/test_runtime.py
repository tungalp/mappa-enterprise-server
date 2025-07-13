import json
from random import random
import uuid
import pytest

from mapa.core.data.json_encoder import JsonEncoder
from mapa.service.function import FunctionRequest
from .conftest import RuntimeAppFixture


@pytest.mark.asyncio
async def test_runtime(fixture: RuntimeAppFixture):
    """Openid scope ile"""
    async with fixture.client() as client:
        function_request = FunctionRequest(
            handler="test:test",
            timeout=30,
            id=str(uuid.uuid4()),
            method='GET',
            raw_path="/test/test/",
            path="/test/test/",
            path_params={},
        )
        content = json.dumps(function_request.model_dump(), cls=JsonEncoder)

        runtime_id = str(uuid.uuid4())
        task_response = await client.post(f"/task/{runtime_id}", content=content)
        assert task_response.status_code == 200
