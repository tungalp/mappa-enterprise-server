import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_app():
    assert 1 == 1