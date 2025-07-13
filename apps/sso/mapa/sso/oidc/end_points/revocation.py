from pydantic import BaseModel


class RevocationEndpoint(BaseModel):
    """Revocation servis metodu parametreleri
    """

    token: str
    token_type_hint: str | None = "refresh_token"

    client_id: str | None = None
    client_secret: str | None = None