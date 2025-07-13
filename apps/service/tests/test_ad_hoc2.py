import json
from random import random
from urllib.parse import urlencode
import pytest



@pytest.mark.asyncio
async def test_adhoc_read_il_list(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["openid"])
    async with fixture.client() as client:
        endpoint = "/admin/idari/il"
        client.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        response = await client.get(endpoint)

    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert len(data["data"]) > 0
  