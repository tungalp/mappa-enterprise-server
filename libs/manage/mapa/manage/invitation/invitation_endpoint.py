from typing import Optional
from pydantic import BaseModel


class InvitationEndpoint(BaseModel):

    email: str
    lang: str
    organization_id :str
