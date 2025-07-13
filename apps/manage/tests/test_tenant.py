import pytest


@pytest.mark.asyncio
async def test_get_tenant_list(fixture):
    
    async with fixture.client() as client:
        token = fixture.create_token()
        user_id = str(fixture.user_id)
        client.headers = {
            "Authorization": f"Bearer {token}"
        }
        response = await client.get(f"/api/manage/tenant/")
     
    assert response.status_code == 200

