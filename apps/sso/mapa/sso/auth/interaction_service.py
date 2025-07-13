from datetime import datetime, timedelta
from mapa.core.data.base_service import BaseService
from mapa.sso.consent.consent_service import ConsentService
from mapa.sso.constants import LevelTypes, PromptModes, StandardScopes
from mapa.sso.oidc.response_handling.interaction_response import InteractionResponse
from mapa.sso.oidc.validation.authorize_request import AuthorizeRequest


class InteractionService(BaseService):
    """Kullanıcı etkileşimi ile ilgili servis
    """

    def __init__(self, consent_service: ConsentService) -> None:
        self._consent_service = consent_service
        super().__init__()

    def process_signup(self, authorize_request: AuthorizeRequest) -> InteractionResponse | None:
        screen_hint = authorize_request.screen_hint
        if screen_hint and screen_hint == "register":
            return InteractionResponse(
                prompt=PromptModes.REGISTER,
                redirect_uri=authorize_request.redirect_uri)
        return None

    def process_login(self, authorize_request: AuthorizeRequest) -> InteractionResponse | None:
        """Login ekranınn çağrılıp çağrılmayacağına karar verir
        """
        ret_val = InteractionResponse(
            prompt=PromptModes.LOGIN,
            redirect_uri=authorize_request.redirect_uri)
        # Kullanıcı tanımlı değilse login istenir
        if not authorize_request.user_session:
            return ret_val
        # Gelen istekte login talebi varsa oturum bilgisine bakılmaksızın login istenir
        if (PromptModes.LOGIN in authorize_request.prompt_modes):
            return ret_val
        # Session varsa ve athenticate olmadıysa login istenir
        if not authorize_request.user_session.authenticated:
            return ret_val
        # Session süresi dolmuşsa login istenir
        if authorize_request.user_session.expired_at < datetime.now():
            return ret_val
        # Session süresi izin verilen max süreyi geçmişse login istenir
        if authorize_request.max_age > 0:
            max_time = authorize_request.user_session.authenticated_at + \
                timedelta(seconds=authorize_request.max_age)
            if max_time > datetime.now():
                return ret_val
        return None

    def process_select_account(self, authorize_request: AuthorizeRequest) -> InteractionResponse | None:
        """Birden fazla account olması durumunda kullanıcı seçim ekranının çağrılması"""
        # Gelen istekte kullanıcı seçim talebi varsa select_account istenir
        if (PromptModes.SELECT_ACCOUNT in authorize_request.prompt_modes):
            return InteractionResponse(
                prompt=PromptModes.SELECT_ACCOUNT,
                redirect_uri=authorize_request.redirect_uri)
        return None

    async def process_consent(self, authorize_request: AuthorizeRequest) -> InteractionResponse | None:
        """Gelen kullanıcı için Onay ekranının gösterilmesi"""
        ret_val = InteractionResponse(
            prompt=PromptModes.CONSENT,
            redirect_uri=authorize_request.redirect_uri)

        # Gelen istekte onay talebi varsa onay istenir. Mevcutta onaylanmış olması
        # durumu değiştirmez
        if (PromptModes.CONSENT in authorize_request.prompt_modes):
            return ret_val

        # Client sistem uygulaması ise onay istenmez
        if authorize_request.client.level_type == LevelTypes.FIRST_PARTY:
            return None

        # Client onay talep etmemişse onay isteği gerekmez
        if not authorize_request.client.require_consent:
            return None

        # Herhangi bir izin yoksa onay istenmez
        if len(authorize_request.scopes) == 0:
            return None

        # Mevcut onay durumu kontrol edilir
        consent = await self._consent_service.find_by_keys(
            authorize_request.client.id,
            authorize_request.user_session.user_id
        )
        # Onay yoksa onay istenir
        if not consent:
            return ret_val
        else:
            # Daha önce kabul edilmemişse onay istenir
            if not consent.accepted:
                return ret_val
            # Daha önce onay verilen izinlerde biz değişiklik olup olmadığı kontrol edilir
            # Eğer değişiklik varsa yeniden onay istenir.
            if len(consent.scopes) > 0:
                intersection = list(
                    set(authorize_request.scopes) & set(consent.scopes))
                return ret_val if len(intersection) != len(authorize_request.scopes) else None

        # offline_access için mutlaka onay istenir
        if StandardScopes.OFFLINE_ACCESS in authorize_request.scopes:
            return ret_val

        return None

    async def process_mfa(self, authorize_request: AuthorizeRequest) -> InteractionResponse | None:
        """Multi Factor Authentication Kontrol edilir"""
        return None
