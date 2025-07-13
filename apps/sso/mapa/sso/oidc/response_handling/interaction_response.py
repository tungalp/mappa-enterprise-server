from typing import Optional
from pydantic import BaseModel


class InteractionResponse(BaseModel):
    """Authorize servis metodu kullanıcı etkileşimi dönüş değeri"""

    redirect_uri: str
    prompt: str | None = None
    state: str | None = None
