from dependency_injector import containers
from dependency_injector import providers

from mapa.sso.consent.consent_service import ConsentService


class ConsentContainer(containers.DeclarativeContainer):
    """Kullanıcı Onay konfigürasyonu"""

    database = providers.Dependency()

    consent_service = providers.Factory(
        ConsentService,
        async_db=database
    )
