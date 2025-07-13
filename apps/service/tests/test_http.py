import json
from random import random
from urllib.parse import urlencode
import pytest


@pytest.mark.asyncio
async def test_http_read_parsel_list(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["openid"])
    async with fixture.client() as client:
        endpoint = "/admin/parsel/?ada_no=100&parsel_no=3"
        client.headers = {
            "Authorization": f"Bearer {token}"
        }
        response = await client.get(endpoint)

    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert len(data) > 0

@pytest.mark.asyncio
async def test_http_read_parsel(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["read:parsel"])
    async with fixture.client() as client:
        endpoint = "/admin/parsel/3"
        client.headers = {
            "Authorization": f"Bearer {token}"
        }
        response = await client.get(endpoint)

    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert data is not None

   
@pytest.mark.asyncio
async def test_http_create_parsel(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["create:parsel"])
    async with fixture.client() as client:
        endpoint = "/admin/parsel/"
        client.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        data = {
            "ada_no": str(100 + int(random() * 100)),
            "parsel_no": str(int(random() * 100)),
            "alan": random() * 10000
        }
        response = await client.post(endpoint, content=json.dumps(data))

    assert response.status_code == 200
    
    
@pytest.mark.asyncio
async def test_http_create_parsel_url_encoded(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["create:parsel"])
    async with fixture.client() as client:
        endpoint = "/admin/parsel/"
        client.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {token}"
        }
        data = {
            "ada_no": str(100 + int(random() * 100)),
            "parsel_no": str(int(random() * 100)),
            "alan": random() * 10000
        }
        response = await client.post(endpoint, content=urlencode(data))

    assert response.status_code == 200
    
    
@pytest.mark.asyncio
async def test_http_update_parsel(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["update:parsel"])
    async with fixture.client() as client:
        endpoint = "/admin/parsel/3"
        client.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        data = {
            "ada_no": str(100 + int(random() * 100)),
            "parsel_no": str(int(random() * 100)),
            "alan": random() * 10000
        }
        response = await client.put(endpoint, content=json.dumps(data))

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_http_delete_parsel(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["delete:parsel"])
    async with fixture.client() as client:
        endpoint = "/admin/parsel/3"
        client.headers = {
            "Authorization": f"Bearer {token}"
        }
        response = await client.delete(endpoint)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_http_any_method(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["delete:parsel"])
    async with fixture.client() as client:
        endpoint = "/admin/parsel/any"
        client.headers = {
            "Authorization": f"Bearer {token}"
        }
        response = await client.get(endpoint)
        assert response.status_code == 200
        data = json.loads(response.content.decode("utf-8"))
        assert data["method"] == "GET"
        
        response = await client.post(endpoint)
        assert response.status_code == 200
        data = json.loads(response.content.decode("utf-8"))
        assert data["method"] == "POST"
        
        response = await client.put(endpoint)
        assert response.status_code == 200
        data = json.loads(response.content.decode("utf-8"))
        assert data["method"] == "PUT"
        
        response = await client.delete(endpoint)
        assert response.status_code == 200
        data = json.loads(response.content.decode("utf-8"))
        assert data["method"] == "DELETE"


        response = await client.patch(endpoint)
        assert response.status_code == 200
        data = json.loads(response.content.decode("utf-8"))
        assert data["method"] == "PATCH"

        response = await client.head(endpoint)
        assert response.status_code == 200

        response = await client.options(endpoint)
        assert response.status_code == 200

