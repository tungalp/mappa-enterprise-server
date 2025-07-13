import pytest
from uuid import uuid4
from mapa.test.base_app_fixture import BaseAppFixture

@pytest.mark.asyncio
async def test_app():
    # TODO (kgulenc) BaseAppFixture test eklenecek
    assert 1 == 1