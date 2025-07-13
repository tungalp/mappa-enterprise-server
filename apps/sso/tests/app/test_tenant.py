import json
import pytest
from ..data import tenant_2_id

    
@pytest.mark.asyncio
async def test_change_tenant(fixture):
    """UserInfo"""
    token = fixture.create_token(["openid"])
    async with fixture.client() as http_client:
        http_client.headers = {
            "Authorization": f"Bearer {token}"
        }
        http_client.cookies = {
            "_sso_session_": fixture.session
        }        
        response = await http_client.post("/api/sso/tenant/", content=json.dumps({
            "client_id": "client_id_manage",
            "tenant_id": str(tenant_2_id)
        }))

    assert response.status_code == 200
    