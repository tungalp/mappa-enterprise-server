import pytest


@pytest.mark.asyncio
async def test_ping(fixture):
    """Ping metodunu test eder """

    async with fixture.client() as client:
        response = await client.get("/api/manage/ping/")

    assert response.status_code == 200
    assert response.json() == {
        "ping": "pong"
    }

# @pytest.mark.asyncio
# async def test_tenant_id_not_found(fixture):
#     """Tenant-Id değerinin olmadığı durumudaki hatayı test eder """
#     async with fixture.client() as client:
#         response = await client.get("/api/manage/ping/")

#     assert response.status_code == 400


@pytest.mark.asyncio
async def test_tenant_id(fixture):
    """Tenant-Id değerinin olmadığı durumudaki hatayı test eder """
    async with fixture.client() as client:
        client.headers.update({
            "Tenant-Id": "10a2238f-4d1e-4626-9f3c-799d3ef5e96d"
        })
        response = await client.get("/api/manage/ping/")

    assert response.status_code == 200
