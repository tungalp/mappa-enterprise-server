import pytest
from urllib import parse


@pytest.mark.asyncio
async def test_authorize_post(fixture):
    """Session Id yokken authorize testi"""

    async with fixture.client() as client:
        client.headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        authorize_endpoint = fixture.create_authorize_endpoint()
        data_dict = {k: v for k, v in vars(
            authorize_endpoint).items() if v is not None}
        data = parse.urlencode(data_dict)
        response = await client.post("/api/sso/oidc/authorize", content=data)

    assert response.status_code == 302


@pytest.mark.asyncio
async def test_authorize_get(fixture):
    """Session Id yokken authorize testi"""

    async with fixture.client() as client:
        authorize_endpoint = fixture.create_authorize_endpoint()
        data_dict = {k: v for k, v in vars(
            authorize_endpoint).items() if v is not None}
        data = parse.urlencode(data_dict)
        response = await client.get(f"/api/sso/oidc/authorize?{data}")

    assert response.status_code == 302


@pytest.mark.asyncio
async def test_authorize_get_wrong_redirect_uri(fixture):
    """Session Id yokken authorize testi"""

    async with fixture.client() as client:
        authorize_endpoint = fixture.create_authorize_endpoint()
        authorize_endpoint.redirect_uri = "http://wrong_redirect_uri"
        data_dict = {k: v for k, v in vars(
            authorize_endpoint).items() if v is not None}
        data = parse.urlencode(data_dict)
        response = await client.get(f"/api/sso/oidc/authorize?{data}")

    assert response.status_code == 302 and response.has_redirect_location


@pytest.mark.asyncio
async def test_authorize_code_flow(fixture):
    """Authorization Code Flow akışına göre Authentication testi"""

    async with fixture.client() as client:
        # Genel akışta kullanılacak olan autorize bilgileri
        authorize_endpoint = fixture.create_authorize_endpoint()
        data_dict = {k: v for k, v in vars(
            authorize_endpoint).items() if v is not None}
        data = parse.urlencode(data_dict)
        response = await client.get(f"/api/sso/oidc/authorize?{data}")
        assert response.status_code == 302
        assert response.headers.get("set-cookie") is not None

        # Login
        session = response.headers.get("set-cookie").split(";")[0].replace("_sso_session_=", "")
        login_endpoint = fixture.create_login_endpoint()
        client.headers = {
            "Content-Type": "application/json",
        }
        client.cookies = {
            "_sso_session_": session
        }
        response = await client.post("/api/sso/auth/login", content=login_endpoint.json(exclude_none=True))
        assert response.status_code == 200
        
        # Authorize response_mode = html
        authorize_endpoint.response_mode = "web_message"
        data_dict = {k: v for k, v in vars(
            authorize_endpoint).items() if v is not None}
        data = parse.urlencode(data_dict)
        response = await client.get(f"/api/sso/oidc/authorize?{data}")

        assert response.status_code == 200
        assert "html" in response.content.decode()



@pytest.mark.asyncio
async def test_authorize_code_web_message(fixture):
    """Authorization Code Flow akışına göre Authentication testi"""

    async with fixture.client() as client:
        # Genel akışta kullanılacak olan autorize bilgileri
        authorize_endpoint = fixture.create_authorize_endpoint()
        authorize_endpoint.response_mode = "web_message"
        data_dict = {k: v for k, v in vars(
            authorize_endpoint).items() if v is not None}
        data = parse.urlencode(data_dict)
        response = await client.get(f"/api/sso/oidc/authorize?{data}")

    assert response.status_code == 302