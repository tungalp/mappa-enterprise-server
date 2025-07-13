import json
from random import choice, random
import pytest

from mapa.core.data.query_args import Filter, FilterOp, QueryArgs


@pytest.mark.asyncio
async def test_adhoc_read_kisi_paging_query_param(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["openid"])
    async with fixture.client() as client:
        query_args = QueryArgs(
            limit=5,
            select=["id", "ad", "soyad"],
            where=[
                Filter(field="ilce_id", op=FilterOp.MORE_THAN, value=1)
            ],
            order={
                "ad": "asc"
            })
        endpoint = f"/admin/kisi/crud?query={query_args.model_dump_json()}"
        client.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        response = await client.get(endpoint)

    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert len(data["items"]) > 0


@pytest.mark.asyncio
async def test_adhoc_create_kisi(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["create:kisi"])
    async with fixture.client() as client:
        endpoint = "/admin/kisi/crud"
        client.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        ad = "Ad" + "_" + str(int(random() * 1000))
        soyad = "Soyad" + "_" + str(int(random() * 1000))
        data = {
            "ad": ad,
            "soyad": soyad,
            "ev_adres_id": 1,
            "is_adres_id": 2,
            "ilce_id": 1
        }
        response = await client.post(endpoint, content=json.dumps(data))

    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert data["affected"] == 1
    assert data["items"][0]["ad"] == ad
    assert data["items"][0]["soyad"] == soyad

@pytest.mark.asyncio
async def test_adhoc_create_kisi_list(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["create:kisi"])
    async with fixture.client() as client:
        endpoint = "/admin/kisi/crud"
        client.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        start = 1
        stop = 11
        data = [{
            "ad": f"Ad {i}",
            "soyad": f"Soyad {i}",
            "ev_adres_id": choice(range(1, 5)),
            "is_adres_id": choice(range(1, 5)),
            "ilce_id": choice(range(1, 5))
        } for i in range(start, stop)]
        response = await client.post(endpoint, content=json.dumps(data))

    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert data["affected"] == (stop - start)


@pytest.mark.asyncio
async def test_adhoc_update_kisi(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["create:kisi", "update:kisi"])
    async with fixture.client() as client:
        query_args = QueryArgs(
            where=[
                # Filter(field="ilce_id.il_id.id", op=FilterOp.EQUAL, value=1)
                Filter(field="is_adres_id", op=FilterOp.EQUAL, value=8)
            ]
        )
        variable = choice(range(1, 100))
        data = {
            "ad": f"Ad {variable}",
            "soyad": f"Soyad {variable}",
            "ev_adres_id": choice(range(1, 5)),
            # "is_adres_id": choice(range(1, 5)), # Sorgulandığı için değiştirilmeyecek
            "ilce_id": choice(range(1, 5))
        }        
        
        # update endpoint
        endpoint = f"/admin/kisi/crud?query={query_args.model_dump_json()}"
        client.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        update_response = await client.put(endpoint, content=json.dumps(data))
        assert update_response.status_code == 200
        update_data = json.loads(update_response.content.decode("utf-8"))
        assert update_data["affected"] == 1

@pytest.mark.asyncio
async def test_adhoc_delete_kisi(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["create:kisi", "update:kisi", "delete:kisi"])
    async with fixture.client() as client:
        endpoint = "/admin/kisi/crud"
        client.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        start = 1
        stop = 11
        data = [{
            "ad": f"Ad {i}",
            "soyad": f"Soyad {i}",
            "ev_adres_id": choice(range(1, 5)),
            "is_adres_id": choice(range(1, 5)),
            "ilce_id": choice(range(1, 5))
        } for i in range(start, stop)]
        create_response = await client.post(endpoint, content=json.dumps(data))
        assert create_response.status_code == 200
        create_data = json.loads(create_response.content.decode("utf-8"))

        ids = [item["id"] for item in create_data["items"]]
        query_args = QueryArgs(
            select=["id"],
            where=[
                Filter(field="id", op=FilterOp.IN, value=ids)
            ])
        # delete endpoint
        endpoint = f"/admin/kisi/crud?query={query_args.json()}"
        client.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        delete_response = await client.delete(endpoint)
        assert delete_response.status_code == 200
        delete_data = json.loads(delete_response.content.decode("utf-8"))
        deleted_ids = [item["id"] for item in delete_data["items"]]
        assert ids.sort() == deleted_ids.sort()
