import json
from random import choice
from urllib.parse import urlencode
import pytest
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.db import Database
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs

from service.integration_handler.table_repository import TableDesc, TableRepository


def create_repo(db_url: str, table_name: str, parent_col_name: str | None = None) -> TableRepository:
    db = Database(db_url)
    return TableRepository(db, TableDesc(table_name, parent_col_name))


@pytest.mark.asyncio
async def test_create_repo(fixture):
    table_name = "adhoc.kisi"
    repo = create_repo(fixture.gw_db_url, table_name)

    assert repo is not None
    assert repo.table is not None


@pytest.mark.asyncio
async def test_find_kisi(fixture):
    table_name = "adhoc.kisi"
    repo = create_repo(fixture.gw_db_url, table_name)

    query_args = QueryArgs(
        select=[
            "ilce_id.il_id", "ilce_id.il_id.id", "ilce_id.il_id.ad",
            "ev_adres_id", "ev_adres_id.id", "ev_adres_id.kapi_no",
            "id", "ad", "soyad",
            "ilce_id", "ilce_id.id", "ilce_id.ad",
            "is_adres_id", "is_adres_id.id", "is_adres_id.kapi_no",
        ],
        where=[
            Filter(field="ilce_id.il_id.id", op=FilterOp.MORE_THAN, value=1)
        ],
        order={
            "ilce_id.ad": "desc"
        }
    )
    count = repo.count(query_args)
    items = repo.find(query_args)
    result = repo.paging(query_args)

    assert result is not None
    assert result.total == count
    assert len(result.items) == len(items)


@pytest.mark.asyncio
async def test_create_kisi(fixture):
    table_name = "adhoc.kisi"
    repo = create_repo(fixture.gw_db_url, table_name)

    value = {
        "ad": "Ad X",
        "soyad": "Soyad X",
        "ev_adres_id": choice(range(1, 5)),
        "is_adres_id": choice(range(1, 5)),
        "ilce_id": choice(range(1, 5)),
        "parent_id": choice(range(1, 5))
    }

    result = repo.create(value)

    assert result is not None
    assert result.success
    assert result.affected == 1
    

@pytest.mark.asyncio
async def test_create_kisi_list(fixture):
    table_name = "adhoc.kisi"
    repo = create_repo(fixture.gw_db_url, table_name)

    start = 1
    stop = 11
    values = [{
        "ad": f"Ad {i}",
        "soyad": f"Soyad {i}",
        "ev_adres_id": choice(range(1, 5)),
        "is_adres_id": choice(range(1, 5)),
        "ilce_id": choice(range(1, 5))
    } for i in range(start, stop)]

    result = repo.create(values)

    assert result is not None
    assert result.success
    assert result.affected == len(range(start, stop))


@pytest.mark.asyncio
async def test_update_kisi_query(fixture):
    table_name = "adhoc.kisi"
    repo = create_repo(fixture.gw_db_url, table_name)

    query_args = QueryArgs(
        where=[
            # Filter(field="ilce_id.il_id.id", op=FilterOp.EQUAL, value=1)
            Filter(field="is_adres_id", op=FilterOp.EQUAL, value=8)
        ]
    )
    variable = choice(range(1, 100))
    value = {
        "ad": f"Ad {variable}",
        "soyad": f"Soyad {variable}",
        "ev_adres_id": choice(range(1, 5)),
        # "is_adres_id": choice(range(1, 5)), # Sorgulandığı için değiştirilmeyecek
        "ilce_id": choice(range(1, 5))
    }
    result = repo.update_with_query(query_args, value)

    assert result is not None
    assert result.affected is not None
    assert result.affected > 0


@pytest.mark.asyncio
async def test_update_kisi_list(fixture):
    table_name = "adhoc.kisi"
    repo = create_repo(fixture.gw_db_url, table_name)

    variable = choice(range(1, 100))
    values = [{
        "id": 1,
        "ad": f"Ad Updated {variable}",
        "soyad": f"Soyad Updated {variable}",
        "ev_adres_id": choice(range(1, 5)),
        # "is_adres_id": choice(range(1, 5)),
        "ilce_id": choice(range(1, 5))
    }, {
        "id": 2,
        "ad": f"Ad Updated {variable}",
        "soyad": f"Soyad Updated {variable}",
        "ev_adres_id": choice(range(1, 5)),
        # "is_adres_id": choice(range(1, 5)),
        "ilce_id": choice(range(1, 5))
    }]

    result = repo.update(values)

    assert result is not None
    assert result.affected is not None
    assert result.affected > 0


@pytest.mark.asyncio
async def test_update_without_query_args(fixture):
    table_name = "adhoc.kisi"
    repo = create_repo(fixture.gw_db_url, table_name)

    with pytest.raises(ValueError) as err:
        result = repo.update_with_query(QueryArgs(), {})


@pytest.mark.asyncio
async def test_delete_kisi(fixture):
    table_name = "adhoc.kisi"
    repo = create_repo(fixture.gw_db_url, table_name)

    query_args = QueryArgs(
        where=[
            Filter(field="is_adres_id", op=FilterOp.EQUAL, value=4),
            Filter(field="id", op=FilterOp.MORE_THAN, value=4)
        ]
    )
    count = repo.count(query_args)
    result = repo.delete(query_args)

    assert result is not None
    assert result.affected == count
    
    
@pytest.mark.asyncio
async def test_delete_kisi2_all(fixture):
    table_name = "adhoc.kisi2"
    repo = create_repo(fixture.gw_db_url, table_name)

    query_args = QueryArgs(
        where=[
            Filter(field="id", op=FilterOp.MORE_THAN, value=0)
        ]
    )
    count = repo.count(query_args)
    result = repo.delete(query_args)

    assert result is not None
    assert result.affected == count    
    
@pytest.mark.asyncio
async def test_find_kisi_recursive(fixture):
    table_name = "adhoc.kisi"
    repo = create_repo(fixture.gw_db_url, table_name, "parent_id")

    query_args = QueryArgs(
        offset=3,
        limit=5,
        select=[
            "ilce_id.il_id", "ilce_id.il_id.id", "ilce_id.il_id.ad",
            "ev_adres_id", "ev_adres_id.id", "ev_adres_id.kapi_no",
            "id", "ad", "soyad",
            "ilce_id", "ilce_id.id", "ilce_id.ad",
            "is_adres_id", "is_adres_id.id", "is_adres_id.kapi_no",
        ],
        where=[
            Filter(field="ilce_id", op=FilterOp.IN, value=[1])
        ],
        order={
            "ad": "desc",
            "ilce_id.il_id.ad": "asc"
        }
    )
    items = repo.find_recursive(query_args)

    assert items is not None
    assert len(items) > 0
    
    
@pytest.mark.asyncio
async def test_find_kisi_recursive_null(fixture):
    table_name = "adhoc.kisi"
    repo = create_repo(fixture.gw_db_url, table_name, "parent_id")

    query_args = QueryArgs(
        offset=3,
        limit=5,
        select=[
            "ilce_id.il_id", "ilce_id.il_id.id", "ilce_id.il_id.ad",
            "ev_adres_id", "ev_adres_id.id", "ev_adres_id.kapi_no",
            "id", "ad", "soyad",
            "ilce_id", "ilce_id.id", "ilce_id.ad",
            "is_adres_id", "is_adres_id.id", "is_adres_id.kapi_no",
        ],
        where=[
        ],
        order={
            "is_adres_id.kapi_no": "desc"
        }
    )
    items = repo.find_recursive(query_args)

    assert items is not None
    assert len(items) > 0    
    
    
    
@pytest.mark.asyncio
async def test_create_kisi_nested(fixture):
    table_name = "adhoc.kisi"
    repo = create_repo(fixture.gw_db_url, table_name)

    start = 1
    stop = 11
    values = [{
        "ad": f"Ad {i}",
        "soyad": f"Soyad {i}",
        "ev_adres_id": {
            "id": choice(range(1, 5))
        },
        "is_adres_id": choice(range(1, 5)),
        "ilce_id": {
            "id": choice(range(1, 5))
        }
    } for i in range(start, stop)]

    result = repo.create(values)

    assert result is not None
    assert result.success
    assert result.affected == len(range(start, stop))    