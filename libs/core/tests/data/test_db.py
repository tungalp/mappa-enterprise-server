import pytest
from mapa.core import __version__
from mapa.core.data.db import Database
from mapa.core.data.async_db import AsyncDatabase
from ..conftest import CoreFixture


def test_db(fixture: CoreFixture):
    """Veritabanı bağlantı testi
    """
    sync_db: Database = Database(fixture.db_url_init)
    with sync_db.session() as session:
        assert session is not None


@pytest.mark.asyncio
async def test_async_db(fixture: CoreFixture):
    """Asenkron veritabanı bağlantı testi
    """
    async_db: AsyncDatabase = fixture.create_db_instance(fixture.db_url_async_init)
    
    created = await fixture.create_database(async_db)
    assert created is True

@pytest.mark.asyncio
async def test_create_test_data(fixture: CoreFixture):
    """Asenkron veritabanı bağlantı testi
    """
    created = await fixture.create_test_data()
    assert created is True