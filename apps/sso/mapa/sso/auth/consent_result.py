from urllib import parse
from mapa.sso.auth.consent_endpoint import ConsentEndpoint
from mapa.sso.consent.consent_model import Consent


class ConsentResult:
    """Consent işleminin dönüş değeri"""

    def __init__(self, api_host: str, consent_endpoint: ConsentEndpoint, consent: Consent) -> None:
        self._api_host = api_host
        self._consent_endpoint = consent_endpoint
        self._consent = consent

    def execute(self):
        req_dict = {k: v for k, v in vars(
            self._consent_endpoint).items() if v is not None}
        del req_dict["accepted"]
        
        url: str = ""
        # Eğer onaylanmışsa authorize işlemine devam edilir.
        if self._consent.accepted:
            url = f"{self._api_host}/api/sso/oidc/authorize?{parse.urlencode(req_dict)}"
        else:
            # Onay gelmemişse hata döndürülür.
            url = f"{self._consent_endpoint.redirect_uri}?error=access_denied&state={self._consent_endpoint.state}"
            
        return {
            "type": "redirect",
            "url": url
        }