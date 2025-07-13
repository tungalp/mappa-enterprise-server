from random import random
import pytest
from urllib import parse
from mapa.sso.auth.mail_service import MailService
from .conftest import SsoFixture


async def create_service(fixture: SsoFixture) -> MailService:
    return MailService(
        smtp="smtp-mail.outlook.com",
        port= 587,
        user_name="trizone@outlook.com.tr",
        password="ki14uRXvi0FYrAye3gwE2",
        method='STARTTLS'
    )


async def create_service_gmail(fixture: SsoFixture) -> MailService:
    return MailService(
        smtp="smtp.gmail.com",
        port= 587,
        user_name="espnoreply20@gmail.com",
        password="yljlspbmvfzprvqw",
        method='STARTTLS'
    )

@pytest.mark.asyncio
async def test_create_service(fixture: SsoFixture):
    """Service"""

    service: MailService = await create_service(fixture)
    assert service is not None


@pytest.mark.asyncio
async def test_send_verify_email_tr(fixture: SsoFixture):
    """Service"""

    service: MailService = await create_service(fixture)
    assert service is not None

    await service.send_verify_email('kuntaygulenc@gmail.com', 'tr')
    


@pytest.mark.asyncio
async def test_send_verify_email_en(fixture: SsoFixture):
    """Service"""

    service: MailService = await create_service(fixture)
    assert service is not None

    await service.send_verify_email('kuntaygulenc@gmail.com', 'en')


@pytest.mark.asyncio
async def test_send_forgot_password_tr(fixture: SsoFixture):
    """Service"""

    service: MailService = await create_service(fixture)
    assert service is not None

    await service.send_forgot_password('kuntaygulenc@gmail.com', '',  'tr')


@pytest.mark.asyncio
async def test_send_forgot_password_en(fixture: SsoFixture):
    """Service"""

    service: MailService = await create_service(fixture)
    assert service is not None

    await service.send_forgot_password('kuntaygulenc@gmail.com', '', 'en')

