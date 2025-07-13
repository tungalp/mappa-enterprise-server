from uuid import uuid4
import pytest
from random import random
from ..data import client_manage


@pytest.mark.asyncio
async def test_register_new(fixture):
    """Yeni kullanıcı oluşturma testi"""

    async with fixture.client() as client:
        register_endpoint = fixture.create_register_endpoint()
        register_endpoint.email = f"{int(random()*1000)}_{register_endpoint.email}"
        client.headers = {
            "Content-Type": "application/json",
        }
        client.cookies = {
            "_sso_session_": fixture.session
        }

        response = await client.post("/api/sso/auth/register", content=register_endpoint.model_dump_json(exclude_none=True))

    assert response.status_code == 200
    assert "code=" in str(response.content)



@pytest.mark.asyncio
async def test_register_existing(fixture):
    """Varolan bir kullanıcı email adresiyle yeni bir kullanıcı oluşturma"""

    async with fixture.client() as client:
        register_endpoint = fixture.create_register_endpoint()
        client.headers = {
            "Content-Type": "application/json",
        }
        client.cookies = {
            "_sso_session_": fixture.session
        }
        with pytest.raises(Exception):
            response = await client.post("/api/sso/auth/register", content=register_endpoint.model_dump_json(exclude_none=True))
            assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_success(fixture):
    """Login testi"""

    async with fixture.client() as client:
        login_endpoint = fixture.create_login_endpoint()
        client.headers = {
            "Content-Type": "application/json",
        }
        client.cookies = {
            "_sso_session_": fixture.session
        }

        response = await client.post("/api/sso/auth/login", content=login_endpoint.model_dump_json(exclude_none=True))

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_login_fail_email(fixture):
    """Hatalı email ile sisteme giriş testi"""

    async with fixture.client() as client:
        login_endpoint = fixture.create_login_endpoint()
        login_endpoint.email = "not_found@exception.com"
        client.headers = {
            "Content-Type": "application/json",
        }
        client.cookies = {
            "_sso_session_": fixture.session
        }
        response = await client.post("/api/sso/auth/login", content=login_endpoint.model_dump_json(exclude_none=True))
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_fail_password(fixture):
    """Hatalı şifre ile sisteme giriş testi"""

    async with fixture.client() as client:
        login_endpoint = fixture.create_login_endpoint()
        login_endpoint.password = "not_match_password"
        client.headers = {
            "Content-Type": "application/json",
        }
        client.cookies = {
            "_sso_session_": fixture.session
        }
        response = await client.post("/api/sso/auth/login", content=login_endpoint.model_dump_json(exclude_none=True))
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_forgot_password_url(fixture):
    """Şifremi unuttum sayfası redirect url adresini kontrol eder """

    async with fixture.client() as client:
        response = await client.get(f"/api/sso/auth/forgot-password/{client_manage.client_id}")

    assert response.status_code == 302


@pytest.mark.asyncio
async def test_forgot_password_mail(fixture):
    """Yeni şifre girişi için mail  gönderilmesi testi"""

    async with fixture.client() as client:
        forgot_password_endpoint = fixture.create_forgot_password_endpoint()
        client.headers = {
            "Content-Type": "application/json",
        }

        response = await client.post("/api/sso/auth/forgot-password", content=forgot_password_endpoint.model_dump_json(exclude_none=True))

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_new_password(fixture):
    """Yeni şifrenin kaydedilmesi"""

    async with fixture.client() as client:
        new_password_endpoint = fixture.create_new_password_endpoint()
        client.headers = {
            "Content-Type": "application/json",
        }

        response = await client.post("/api/sso/auth/new-password", content=new_password_endpoint.model_dump_json(exclude_none=True))

    assert response.status_code == 200
