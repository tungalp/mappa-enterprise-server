import string
import secrets
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.sso.authorization_code.authorization_code_model import AuthorizationCode, CreateAuthorizationCode, UpdateAllAuthorizationCode, UpdateAuthorizationCode
from mapa.sso.authorization_code.authorization_code_repository import AuthorizationCodeRepository


class AuthorizatioCodeService(BaseEntityService[
    AuthorizationCodeRepository, AuthorizationCode, CreateAuthorizationCode, UpdateAuthorizationCode, UpdateAllAuthorizationCode]):
    """AuthorizationCode servisi"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, AuthorizationCodeRepository, AuthorizationCode)

    async def get_by_code(self, code: str, tenant_id: str | None = None) -> AuthorizationCode | None:
        """Code değerine uyan kaydı getirir."""

        return await self.find_one(QueryArgs(
            where=[
                Filter(field="code", op=FilterOp.EQUAL, value=code)
            ]
        ), tenant_id)    


    def generate_code(self, size: int = 64) -> str:
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for i in range(size))
