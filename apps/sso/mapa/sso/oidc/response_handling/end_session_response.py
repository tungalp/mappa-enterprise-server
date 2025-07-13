from typing import List, Optional
from pydantic import BaseModel


class EndSessionResponse(BaseModel):
    """EndSession servis metodu dönüş modeli"""

    redirect_uri: str
    state: str | None = None
