import asyncio
import pytest
from mapa.manage import __version__
from .conftest import ManageFixture, generate_api, generate_client_api, tenant_id, generate_api_scope, generate_client, generate_client_api_scope
from typing import Any, Dict


def test_version():
    assert __version__ == '0.1.0'

@pytest.mark.asyncio
async def test_create(fixture: ManageFixture):
    """"Create"""
    # Test verisi oluşturulur
    initialized = await fixture.create_test_data()
    assert initialized is True