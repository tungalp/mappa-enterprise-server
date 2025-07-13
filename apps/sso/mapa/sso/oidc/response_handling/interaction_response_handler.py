from mapa.sso.auth.interaction_service import InteractionService
from mapa.sso.constants import AuthorizeErrors, PromptModes
from mapa.sso.oidc.response_handling.authorize_error_response import AuthorizeErrorResponse
from mapa.sso.oidc.response_handling.interaction_response import InteractionResponse
from mapa.sso.oidc.validation.authorize_request import AuthorizeRequest


class InteractionResponseHandler:
    """Doğrulanmış authorize isteğini işleyerek uygun olan kullanıcı etkileşim
    arayüzünü değerini oluşturur.
    Mevcut değerler LOGIN, CONSENT, SELECT_ACCCOUNT, REGISTER
    """

    def __init__(self, interaction_service: InteractionService) -> None:
        self._service = interaction_service

    async def create_response(
        self,
        authorize_request: AuthorizeRequest
        ) -> InteractionResponse | AuthorizeErrorResponse | None:
        """Gelen Authorize isteğine karşılık bir kullanıcı etkileşimi
        gerekip gerekmediği kontrol edilir.
        """

        # Gelen isteğin register isteği olup olmadığı kontrol edilir. Eğer register isteği ise
        # register sayfasına yönlendirilir.
        ret_val = self._service.process_signup(authorize_request)
        if ret_val:
            return ret_val

        ret_val = self._service.process_select_account(authorize_request)
        if not ret_val:
            ret_val = self._service.process_login(authorize_request)
            if not ret_val:
                ret_val = await self._service.process_consent(authorize_request)

        if ret_val and PromptModes.NONE in authorize_request.prompt_modes:
            # prompt=none olduğunda arayüz gösterilmeyeceği için ret_val varsa hata döndürülecek
            error_description = AuthorizeErrors.LOGIN_REQUIRED if ret_val.prompt == PromptModes.LOGIN else \
                AuthorizeErrors.CONSENT_REQUIRED if ret_val.prompt == PromptModes.CONSENT else \
                AuthorizeErrors.ACCOUNT_SELECTION_REQUIRED
            ret_val = AuthorizeErrorResponse(
                error=AuthorizeErrors.INTERACTION_REQUIRED,
                error_description=error_description
            )
        # Dönüş değerine durum değişkeni set edilir
        if ret_val:
            ret_val.state = authorize_request.state

        return ret_val
