import json
from random import choice, random
from urllib.parse import urlencode
import pytest

from mapa.core.data.query_args import Filter, FilterOp, QueryArgs


@pytest.mark.asyncio
async def test_adhoc_read_kisi(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["read:kisi"])
    async with fixture.client() as client:
        endpoint = "/admin/kisi/3"
        client.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {token}"
        }
        response = await client.get(endpoint)

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_adhoc_read_kisi_list(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["openid"])
    async with fixture.client() as client:
        endpoint = "/admin/kisi/?ad=%Ad%&soyad=%1%"
        client.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-Test-Header": "Test Header"
        }
        response = await client.get(endpoint)

    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert len(data["data"]) > 0
    
    
@pytest.mark.asyncio
async def test_adhoc_read_kisi_list_query_string(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["openid"])
    async with fixture.client() as client:
        endpoint = "/admin/kisi/?ad=%1%&soyad=%1%"
        client.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        response = await client.get(endpoint)

    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert len(data["data"]) > 0


@pytest.mark.asyncio
async def test_adhoc_create_kisi(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["create:kisi"])
    async with fixture.client() as client:
        endpoint = "/admin/kisi/"
        client.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        data = {
            "ad": "Ad" + "_" + str(int(random() * 1000)),
            "soyad": "Soyad" + "_" + str(int(random() * 1000)),
            "ev_adres_id": choice(range(1, 5)),
            "is_adres_id": choice(range(1, 5)),
            "ilce_id": choice(range(1, 5)),
            "parent_id": choice(range(1, 5)),
            "test": "test"  # Ekstra parametre test amacıyla konuldu. İşlemi etkilemiyor
        }
        response = await client.post(endpoint, content=json.dumps(data))

    assert response.status_code == 200
    
@pytest.mark.asyncio
async def test_adhoc_create_kisi_list(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["create:kisi"])
    async with fixture.client() as client:
        endpoint = "/admin/kisi/"
        client.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        data = [{
            "ad": "Ad" + "_" + str(int(random() * 1000)),
            "soyad": "Soyad" + "_" + str(int(random() * 1000)),
            "ev_adres_id": choice(range(1, 5)),
            "is_adres_id": choice(range(1, 5)),
            "ilce_id": choice(range(1, 5)),
            "parent_id": choice(range(1, 5)),            
        } for i in range(1, 10)]
        response = await client.post(endpoint, content=json.dumps(data))

    assert response.status_code == 200
        
@pytest.mark.asyncio
async def test_adhoc_create_kisi_with_url_encoded(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["create:kisi"])
    async with fixture.client() as client:
        endpoint = "/admin/kisi/"
        client.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {token}"
        }
        data = {
            "ad": "Ad" + "_" + str(int(random() * 1000)),
            "soyad": "Soyad" + "_" + str(int(random() * 1000)),
            "ev_adres_id": choice(range(1, 5)),
            "is_adres_id": choice(range(1, 5)),
            "ilce_id": choice(range(1, 5)),
            "parent_id": choice(range(1, 5)),            
        }
        response = await client.post(endpoint, content=urlencode(data))

    assert response.status_code == 200    
    
@pytest.mark.asyncio
async def test_adhoc_update_kisi(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["create:kisi", "update:kisi"])
    async with fixture.client() as client:
        # insert endpoint
        endpoint = "/admin/kisi/"
        client.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        data = {
            "ad": "Ad" + "_" + str(int(random() * 1000)),
            "soyad": "Soyad" + "_" + str(int(random() * 1000)),
            "ev_adres_id": choice(range(1, 5)),
            "is_adres_id": choice(range(1, 5)),
            "ilce_id": choice(range(1, 5)),
            "parent_id": choice(range(1, 5)),            
        }
        create_response = await client.post(endpoint, content=json.dumps(data))
        assert create_response.status_code == 200
        create_data = json.loads(create_response.content.decode("utf-8"))
        assert create_data["data"][0]["id"]
        
    async with fixture.client() as client:
        # update endpoint
        kisi_id = create_data["data"][0]["id"]
        endpoint = f"/admin/kisi/{kisi_id}"
        client.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }        
        modified_data = {
            "ad": "Ad" + "_" + str(int(random() * 1000)),
            "soyad": "Soyad" + "_" + str(int(random() * 1000)),
        }
        update_response = await client.put(endpoint, content=json.dumps(modified_data))
        assert update_response.status_code == 200
        update_data = json.loads(update_response.content.decode("utf-8"))
        assert update_data["data"][0]["id"] == kisi_id
        assert update_data["data"][0]["ad"] == modified_data["ad"]
        assert update_data["data"][0]["soyad"] == modified_data["soyad"]


@pytest.mark.asyncio
async def test_adhoc_delete_kisi(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["create:kisi", "update:kisi", "delete:kisi"])
    async with fixture.client() as client:
        # insert endpoint
        endpoint = "/admin/kisi/"
        client.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        data = {
            "ad": "Ad" + "_" + str(int(random() * 1000)),
            "soyad": "Soyad" + "_" + str(int(random() * 1000)),
            "ev_adres_id": choice(range(1, 5)),
            "is_adres_id": choice(range(1, 5)),
            "ilce_id": choice(range(1, 5)),
            "parent_id": choice(range(1, 5)),            
        }
        create_response = await client.post(endpoint, content=json.dumps(data))
        assert create_response.status_code == 200
        create_data = json.loads(create_response.content.decode("utf-8"))
        assert create_data["data"][0]["id"]
        
    async with fixture.client() as client:
        # delete endpoint
        kisi_id = create_data["data"][0]["id"]
        endpoint = f"/admin/kisi/{kisi_id}"
        client.headers = {
            "Authorization": f"Bearer {token}"
        }        
        delete_response = await client.delete(endpoint)
        assert delete_response.status_code == 200
        update_data = json.loads(delete_response.content.decode("utf-8"))
        assert update_data["affected"] == 1
            
@pytest.mark.asyncio
async def test_adhoc_wrong_scope(fixture):
    """Kisi listesi için openid token gerekir. email scope ile token 404 döndürmesi gerekir."""
    token = fixture.create_token(["email"])
    async with fixture.client() as client:
        endpoint = "/"
        client.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = await client.get(endpoint)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_adhoc_with_parameter_mapping(fixture):
    """Kişi Listesi parametre eşleştirmesi ile okunur
    Paremetre değiştirme işleminde name -> ad olarak
    surname ise header.X-Test-Header olarak değiştiriliyor.
    Name ve surname query string parametreleri siliniyor.
    Header değeri ise yeni bir değer alıyor
    
    header.X-Test-Header OVERWRITE "Modified-X-Header"
    query.ad APPEND query.name
    query.soyad APPEND header.X-Test-Header
    query.name DELETE
    query.surname DELETE
    """

    token = fixture.create_token(["openid"])
    async with fixture.client() as client:
        endpoint = "/admin/kisi/list?name=%1%&surname=%1%"
        client.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-Test-Header": "Test Header",
            "X-Will-Remove-Header": "Will Remove Header"
        }
        response = await client.get(endpoint)

    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert len(data["data"]) > 0