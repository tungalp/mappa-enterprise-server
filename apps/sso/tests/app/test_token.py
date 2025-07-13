import json
import pytest
from urllib import parse


@pytest.mark.asyncio
async def test_token_auth_code(fixture):
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


@pytest.mark.asyncio
async def test_token_refresh_token(fixture):
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
        assert "refresh_token" in token_response.content.decode("utf-8")
        
        # Refresh Token Request
        refresh_token = json.loads(token_response.content.decode("utf-8"))["refresh_token"]
        refresh_token_endpoint = fixture.create_refresh_token_endpoint(refresh_token)
        data_dict = {k: v for k, v in vars(
            refresh_token_endpoint).items() if v is not None}
        data = parse.urlencode(data_dict)

        response = await client.post("/api/sso/oidc/token", content=data)
        assert response.status_code == 200
        
        
@pytest.mark.asyncio
async def test_token_revocation(fixture):
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
        assert "refresh_token" in token_response.content.decode("utf-8")
        
        # Revocation Request
        base64_auth_string = fixture.create_basic_auth("client_id_manage", "client_secret_manage")
        client.headers.update({
            "Authorization": f"Basic {base64_auth_string}",
        })
        refresh_token = json.loads(token_response.content.decode("utf-8"))["refresh_token"]
        revocation_endpoint = fixture.create_revocation_endpoint(refresh_token)
        data_dict = {k: v for k, v in vars(
            revocation_endpoint).items() if v is not None}
        data = parse.urlencode(data_dict)

        response = await client.post("/api/sso/oidc/revocation", content=data)
        assert response.status_code == 200
