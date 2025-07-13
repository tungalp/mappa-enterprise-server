from typing import Optional
from pydantic import BaseModel


class ForgotPasswordEndpoint(BaseModel):
    """"Şifremi unuttum parametreleri"""

    client_id: str
    email: str
    state: str
    lang: str
    redirect_uri: str
    scope: str
    audience: str
