import json
from random import random
from urllib.parse import urlencode
import pytest
from lxml import etree
from mapa.core.data.query_args import Filter, FilterGroup, FilterOp, FilterType, QueryArgs
from service.integration_handler.spatial.transform_to_cql import TransformToCQL
from service.integration_handler.spatial.transform_to_ogc import TransformToOGC
from service.integration_handler.spatial.wfs_transaction import WfsTransaction


@pytest.mark.asyncio
async def test_wms(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["openid"])
    query_string = "SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&FORMAT=image/png" \
                   "&TRANSPARENT=true&STYLES&LAYERS=:countries&" \
                   "exceptions=application/vnd.ogc.se_inimage&" \
                   "CQL_FILTER=LABELRANK=3&CRS=EPSG:4326&" \
                   "WIDTH=768&HEIGHT=370&" \
                   "BBOX=-53.7890625,-80.5078125,76.2890625,189.4921875"
    async with fixture.client() as client:
        endpoint = f"/admin/spatial/wms?{query_string}"
        client.headers = {
            "Authorization": f"Bearer {token}"
        }
        response = await client.get(endpoint)

    assert response.status_code == 200
    assert len(response.content) > 0
    
@pytest.mark.asyncio
async def test_wfs_get(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["openid"])
    query_args = QueryArgs(
        limit=50,
        where=[
            Filter(field="LABELRANK", op=FilterOp.EQUAL, value=3)
        ],
        order={
            "ADMIN": "asc"
        })
    query_string = "typeName=countries&" \
                   "srsName=EPSG:4326&" \
                   f"query={query_args.model_dump_json()}"
    async with fixture.client() as client:
        endpoint = f"/admin/spatial/wfs?{query_string}"
        client.headers = {
            "Authorization": f"Bearer {token}"
        }
        response = await client.get(endpoint)

    assert response.status_code == 200
    assert len(response.content) > 0
    data = json.loads(response.content.decode("utf-8"))
    assert data is not None

@pytest.mark.asyncio
async def test_wmts(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["openid"])
    type_name = "countries"
    z = 2
    x = 0
    y = 1
    format_type = "png"
    async with fixture.client() as client:
        endpoint = f"/admin/spatial/tile/wmts/{type_name}/{z}/{x}/{y}.{format_type}"
        client.headers = {
            "Authorization": f"Bearer {token}"
        }
        response = await client.get(endpoint)

    assert response.status_code == 200
    assert len(response.content) > 0
    
@pytest.mark.asyncio
async def test_xyz(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["openid"])
    type_name = "nlcd"
    z = 3
    x = 1
    y = 3
    format_type = "png"
    async with fixture.client() as client:
        endpoint = f"/admin/spatial/tile/xyz/{type_name}/{z}/{x}/{y}.{format_type}"
        client.headers = {
            "Authorization": f"Bearer {token}"
        }
        response = await client.get(endpoint)

    assert response.status_code == 200
    assert len(response.content) > 0 
    
@pytest.mark.asyncio
async def test_xyz_2(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["openid"])
    type_name = "nlcd"
    z = 3
    x = 1
    y = 3
    format_type = "png"
    async with fixture.client() as client:
        endpoint = f"/admin/spatial/tile/xyz_2/{type_name}/{z}/{x}/{y}.{format_type}"
        client.headers = {
            "Authorization": f"Bearer {token}"
        }
        response = await client.get(endpoint)

    assert response.status_code == 200
    assert len(response.content) > 0


@pytest.mark.asyncio
async def test_transform_to_cql(fixture):
    test_geom = {
        "type": "Point",
        "coordinates": [40.5, 40.5]
    }
    test_geom_distance = {
        "type": "Point",
        "coordinates": [40.5, 40.5],
        "distance": 100,
        "unit": "meters"
    }
    
    queryArgs: QueryArgs = QueryArgs(where=[
        Filter(field="f1", op=FilterOp.EQUAL, value="val1"),
        Filter(field="f2", op=FilterOp.NOT_EQUAL, value="val1"),
        Filter(field="f3", op=FilterOp.IN, value=[1, 2, 3]),
        Filter(field="f4", op=FilterOp.NOT_IN, value=["val1", "val2"]),
        Filter(field="f5", op=FilterOp.NULL),
        Filter(field="f6", op=FilterOp.NOT_NULL),
        Filter(field="f7", op=FilterOp.LESS_THAN, value=2),
        Filter(field="f8", op=FilterOp.LESS_THAN_OR_EQUAL, value=2),
        Filter(field="f9", op=FilterOp.MORE_THAN, value=3),
        Filter(field="f10", op=FilterOp.MORE_THAN_OR_EQUAL, value=3),
        Filter(field="f11", op=FilterOp.BETWEEN, value=[4, 10]),
        Filter(field="f12", op=FilterOp.BBOX, value=[30, 30, 40, 40]),
        Filter(field="f13", op=FilterOp.EQUALS, value=test_geom),
        Filter(field="f14", op=FilterOp.DISJOINT, value=test_geom),
        Filter(field="f15", op=FilterOp.INTERSECTS, value=test_geom),
        Filter(field="f16", op=FilterOp.TOUCHES, value=test_geom),
        Filter(field="f17", op=FilterOp.CROSSES, value=test_geom),
        Filter(field="f18", op=FilterOp.WITHIN, value=test_geom),
        Filter(field="f19", op=FilterOp.CONTAINS, value=test_geom),
        Filter(field="f20", op=FilterOp.OVERLAPS, value=test_geom),
        Filter(field="f21", op=FilterOp.RELATE, value=test_geom),
        Filter(field="f22", op=FilterOp.DWITHIN, value=test_geom_distance),
        Filter(field="f23", op=FilterOp.BEYOND, value=test_geom_distance),
    ])
    transformer = TransformToCQL()
    query_str = transformer.transform(queryArgs)
    assert len(query_str) > 0
    
@pytest.mark.asyncio
async def test_transform_to_ogc(fixture):
    test_geom = {
        "type": "Point",
        "coordinates": [40.5, 40.5]
    }
    query_args: QueryArgs = QueryArgs(where=[
        Filter(field="f1", op=FilterOp.EQUAL, value="val1"),
        Filter(field="f2", op=FilterOp.NOT_EQUAL, value="val1"),
        FilterGroup(
            type=FilterType.AND,
            filters=[
                Filter(field="f3", op=FilterOp.IN, value=[1, 2, 3]),
                Filter(field="f4", op=FilterOp.NOT_IN, value=["val1", "val2"]),
                Filter(field="f5", op=FilterOp.NULL),
                FilterGroup(
                    type=FilterType.OR,
                    filters=[
                        Filter(field="f6", op=FilterOp.NOT_NULL),
                        Filter(field="f7", op=FilterOp.LESS_THAN, value=2),
                        Filter(field="f8", op=FilterOp.LESS_THAN_OR_EQUAL, value=2),
                    ]
                )
            ]
        ),
        Filter(field="f9", op=FilterOp.MORE_THAN, value=3),
        Filter(field="f10", op=FilterOp.MORE_THAN_OR_EQUAL, value=3),
        Filter(field="f11", op=FilterOp.BETWEEN, value=[4, 10]),
        Filter(field="f12", op=FilterOp.BBOX, value=[30, 30, 40, 40]),
        Filter(field="f13", op=FilterOp.EQUALS, value=test_geom),
        Filter(field="f14", op=FilterOp.CONTAINS, value=test_geom),
        Filter(field="f15", op=FilterOp.DISJOINT, value=test_geom),
        Filter(field="f16", op=FilterOp.INTERSECTS, value=test_geom),
        Filter(field="f17", op=FilterOp.TOUCHES, value=test_geom),
        Filter(field="f19", op=FilterOp.WITHIN, value=test_geom),
        Filter(field="f20", op=FilterOp.CONTAINS, value=test_geom),
        Filter(field="f21", op=FilterOp.OVERLAPS, value=test_geom)
    ])
    transformer = TransformToOGC()
    query_el = transformer.transform(query_args)
    query_str = etree.tostring(query_el)
    assert len(query_str) > 0


@pytest.mark.asyncio
def test_transaction_insert():
    url = "esp"
    transaction = WfsTransaction(url)
    features = [
        {
            "type": "Feature",
            "id": "test_geom.1",
            "geometry": {
                "type": "Point",
                "coordinates": [40.5, 40.5]
            },
            "geometry_name": "geom",
            "properties": {
                "name": "isim 1"
            }
        },
        {
            "type": "Feature",
            "id": "test_geom.2",
            "geometry": {
                "type": "LineString",
                "coordinates": [
                [40.0, 40.0],
                [40.1, 40.1],
                [40.2, 40.2],
                [40.3, 40.3],
                [40.4, 40.4],
                [40.5, 40.5],
                [40.6, 40.6],
                [40.7, 40.7],
                [40.8, 40.8],
                [40.9, 40.9]
                ]
            },
            "properties": {
                "name": "isim 2"
            }
        },
        {
            "type": "Feature",
            "id": "test_geom.3",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                [
                    [40.0, 40.0],
                    [40.0, 41.0],
                    [40.2, 41.0],
                    [40.4, 41.0],
                    [40.6, 41.0],
                    [40.8, 41.0],
                    [41.0, 41.0],
                    [41.0, 40.0],
                    [40.5, 40.0],
                    [40.0, 40.0]
                ]
                ]
            },
            "properties": {
                "name": "isim 3"
            }
        }
    ]
    insert = transaction.insert("esp:test_geom", features)
    assert insert and len(insert) > 0
    
    
    
@pytest.mark.asyncio
def test_transaction_update():
    url = "http://test.com"
    transaction = WfsTransaction(url)
    feature = {
        "type": "Feature",
        "properties": {
            "name": "isim 11",
            "tip": "11"
        }
    }
    query_args = QueryArgs(
        where=[
            Filter(field='id', op=FilterOp.EQUAL, value=1)
        ]
    )
    update = transaction.update("esp:test_geom", feature, query_args)
    
    assert update and len(update) > 0

@pytest.mark.asyncio    
def test_transaction_update_with_geom():
    url = "http://test.com"
    transaction = WfsTransaction(url)
    feature = {
        "type": "Feature",
        "id": "test_geom.1",
        "geometry": {
            "type": "Point",
            "coordinates": [40.01, 40.01]
        },
        "geometry_name": "geom",
        "properties": {
            "name": "isim 11.1"
        }
    }
    query_args = QueryArgs(
        where=[
            Filter(field='id', op=FilterOp.EQUAL, value=1)
        ]
    )    
    update = transaction.update("esp:test_geom", feature, query_args)
    
    assert update and len(update) > 0
    
@pytest.mark.asyncio    
def test_transaction_delete():
    url = "http://test.com"
    transaction = WfsTransaction(url)
    query_args = QueryArgs(
        where=[
            Filter(field='id', op=FilterOp.EQUAL, value=2)
        ]
    )    
    delete = transaction.delete("esp:test_geom", query_args)
    
    assert delete and len(delete) > 0    
    
    
@pytest.mark.asyncio
async def test_wfs_t_insert(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["openid"])
    type_name = "esp:test_geom"
    async with fixture.client() as client:
        endpoint = f"/admin/spatial/transaction?typeName={type_name}"
        client.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data = [
            {
                "type": "Feature",
                "id": "test_geom.1",
                "geometry": {
                    "type": "Point",
                    "coordinates": [40.5, 40.5]
                },
                "geometry_name": "geom",
                "properties": {
                    "name": "isim 1"
                }
            },
            {
                "type": "Feature",
                "id": "test_geom.2",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                    [40.0, 40.0],
                    [40.1, 40.1],
                    [40.2, 40.2],
                    [40.3, 40.3],
                    [40.4, 40.4],
                    [40.5, 40.5],
                    [40.6, 40.6],
                    [40.7, 40.7],
                    [40.8, 40.8],
                    [40.9, 40.9]
                    ]
                },
                "properties": {
                    "name": "isim 2"
                }
            },
            {
                "type": "Feature",
                "id": "test_geom.3",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                    [
                        [40.0, 40.0],
                        [40.0, 41.0],
                        [40.2, 41.0],
                        [40.4, 41.0],
                        [40.6, 41.0],
                        [40.8, 41.0],
                        [41.0, 41.0],
                        [41.0, 40.0],
                        [40.5, 40.0],
                        [40.0, 40.0]
                    ]
                    ]
                },
                "properties": {
                    "name": "isim 3"
                }
            }
        ]
        response = await client.post(endpoint, content=json.dumps(data))

    assert response.status_code == 200
    assert len(response.content) > 0
    
    
@pytest.mark.asyncio
async def test_wfs_t_update(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["openid"])
    type_name = "esp:test_geom"
    async with fixture.client() as client:
        client.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [40.5, 40.5]
            },
            "properties": {
                "name": "isim 1212"
            }
        }
        query_args: QueryArgs = QueryArgs(where=[
            Filter(field="id", op=FilterOp.EQUAL, value=1),
        ])
        query = query_args.model_dump_json()
        endpoint = f"/admin/spatial/transaction?typeName={type_name}&query={query}"
        response = await client.put(f"{endpoint}", content=json.dumps(data))

    assert response.status_code == 200
    assert len(response.content) > 0
    
    
@pytest.mark.asyncio
async def test_wfs_t_delete(fixture):
    """Openid scope ile"""
    token = fixture.create_token(["openid"])
    type_name = "esp:test_geom"
    async with fixture.client() as client:
        client.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        query_args: QueryArgs = QueryArgs(where=[
            Filter(field="id", op=FilterOp.EQUAL, value=44),
        ])
        query = query_args.model_dump_json()
        endpoint = f"/admin/spatial/transaction?typeName={type_name}&query={query}"
        response = await client.delete(f"{endpoint}")

    assert response.status_code == 200
    assert len(response.content) > 0    