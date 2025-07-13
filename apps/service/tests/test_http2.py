import json
from random import random
from urllib.parse import urlencode
import pytest


@pytest.mark.asyncio
async def test_http_read_product_list(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["openid"])
    async with fixture.client() as client:
        endpoint = "/admin/product/list"
        client.headers = {
            "Authorization": f"Bearer {token}"
        }
        response = await client.get(endpoint)

    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert len(data) > 0

@pytest.mark.asyncio
async def test_http_read_product(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["read:product"])
    async with fixture.client() as client:
        endpoint = "/admin/product/item/1"
        client.headers = {
            "Authorization": f"Bearer {token}"
        }
        response = await client.get(endpoint)

    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert data is not None
