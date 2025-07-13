import json
from random import random
from urllib.parse import urlencode
import pytest


@pytest.mark.asyncio
async def test_soap_ping(fixture):
    """Tüm ülkelerin getirilmesi"""
    
    token = fixture.create_token(["openid"])
    async with fixture.client() as client:
        endpoint = "/admin/soap/multiple/deneme?int_param=123"
        client.headers = {
            "content-type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        data = {
            "inputModel": {
                "StringProperty": "string_property",
                "IntProperty": 123,
                "ListProperty": [
                    "str_1", "str_2", "str_3"
                ],
                "DateTimeProperty": "2023-12-12T04:02:09.000",
                "ComplexListProperty": [
                    {"StringProperty": "string_property", "IntProperty": 123},
                    {"StringProperty": "string_property_2", "IntProperty": 1234},
                    {"StringProperty": "string_property_3", "IntProperty": 12345},
                ]
            }
        }
        response = await client.post(endpoint, content=json.dumps(data))

    assert response.status_code == 200
    data = json.loads(response.content.decode("utf-8"))
    assert len(data) > 0

# @pytest.mark.asyncio
# async def test_adhoc_read_product(fixture):
#     """Openid scope ile"""
#     token = fixture.create_token(["read:product"])
#     async with fixture.client() as client:
#         endpoint = "/admin/product/item/1"
#         client.headers = {
#             "Authorization": f"Bearer {token}"
#         }
#         response = await client.get(endpoint)

#     assert response.status_code == 200
#     data = json.loads(response.content.decode("utf-8"))
#     assert data is not None
