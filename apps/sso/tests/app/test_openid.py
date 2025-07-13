import json
import pytest
from urllib import parse

@pytest.mark.asyncio
async def test_jwks(fixture):
    """Token """
    async with fixture.client() as client:
        # Genel akışta kullanılacak olan autorize bilgileri

        response = await client.get("/api/sso/oidc/jwks")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_well_known(fixture):
    """Token """
    async with fixture.client() as client:
        # Genel akışta kullanılacak olan autorize bilgileri

        response = await client.get("/api/sso/oidc/.well-known/openid-configuration")
        assert response.status_code == 200
        
        conf = json.loads(response.content.decode("utf-8"))
        assert conf is not None


@pytest.mark.asyncio
async def test_end_session(fixture):
    """Token """
    async with fixture.client() as client:
        # Genel akışta kullanılacak olan autorize bilgileri
        code_verifier = fixture.auth_util_service.generate_code_verifier()
        code_challenge = fixture.auth_util_service.generate_code_challenge(code_verifier)

        authorize_endpoint = fixture.create_authorize_endpoint(code_challenge)
        authorize_endpoint.code_challenge = code_challenge
        data_dict = {k: v for k, v in vars(
            authorize_endpoint).items() if v is not None}
        data = parse.urlencode(data_dict)
        response = await client.get(f"/api/sso/oidc/authorize?{data}")
        assert response.status_code == 302
        assert response.headers.get("set-cookie") is not None

        # Login
        session = response.headers.get("set-cookie").split(";")[0].replace("_sso_session_=", "")
        login_endpoint = fixture.create_login_endpoint(authorize_endpoint)
        client.headers = {
            "Content-Type": "application/json",
        }
        client.cookies = {
            "_sso_session_": session
        }
        response = await client.post("/api/sso/auth/login", content=login_endpoint.json(exclude_none=True))
        assert response.status_code == 200
        
        # Code Token
        client.headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        code = response.content.decode("utf-8").split("&")[0].split("=")[1]
        token_endpoint = fixture.create_token_auth_code_endpoint(code, code_verifier)
        
        data_dict = {k: v for k, v in vars(
            token_endpoint).items() if v is not None}
        data = parse.urlencode(data_dict)

        token_response = await client.post("/api/sso/oidc/token", content=data)
        assert token_response.status_code == 200

        # End Session
        client.headers = {}
        client.cookies = {
            "_sso_session_": session
        }        
        end_session_endpoint = fixture.create_end_session_endpoint()
        end_session_endpoint.id_token_hint = json.loads(token_response.content.decode("utf-8"))["id_token"]
        data_dict = {k: v for k, v in vars(
            end_session_endpoint).items() if v is not None}
        data = parse.urlencode(data_dict)

        end_session_response = await client.get(f"/api/sso/oidc/endsession?{data}")
        assert end_session_response.status_code == 302
        

@pytest.mark.asyncio
async def test_client_info(fixture):
    """ClientInfo"""
    
    async with fixture.client() as http_client:
        client_id = "client_id_manage"
        response = await http_client.get(f"/api/sso/client/info/{client_id}")

    assert response.status_code == 200
    
@pytest.mark.asyncio
async def test_user_info(fixture):
    """UserInfo"""
    token = fixture.create_token(["openid"])
    async with fixture.client() as http_client:
        http_client.headers = {
            "Authorization": f"Bearer {token}"
        }
        response = await http_client.get("/api/sso/oidc/userinfo")

    assert response.status_code == 200
    