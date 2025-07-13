import json
from typing import List
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.sso.jwk.jwk_model import CreateJwkModel, JwkModel, UpdateAllJwkModel, UpdateJwkModel
from mapa.sso.jwk.jwk_repository import JwkRepository
from jwcrypto.jwk import JWK
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta

JWKS_ROTATION: int= 30

class JwkService(BaseEntityService[JwkRepository, JwkModel, CreateJwkModel, UpdateJwkModel, UpdateAllJwkModel]):
    """JWK Servisi"""

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, JwkRepository, JwkModel)
        
    async def get_active_set(self, limit: int = 2) -> List[JwkModel]:
        """JWK verilerinden aktif olanları getirir. Eğer zaman aşımına uğramış jwk varsa
        yeni bir tane oluştutur ve listeye ekler"""

        # En uzun ömürlü ilk kullanılacak, ömrü az kalanlar kullanılmış olanlar olacaktır.
        # Böylelikle yeni oluşturulan ilk sırada olacağından dolayı şifreleme işlemleri
        # bu ilk anahtarla yapılır. Listede geriye düşenler sadece destekleme amacıyla kalır. 
        jwk_list = await self.find(query_args=QueryArgs(
            limit=limit,
            where=[
                Filter(field="expired_at", op=FilterOp.MORE_THAN, value=datetime.now())
            ],
            order={
                "expired_at": "desc"
            }),
        )
        jwk_count = len(jwk_list)
        if jwk_count < limit:
            for _ in range((limit - jwk_count), 0, -1):
                # Aynı anda oluşturulsa bile birer ay ara ile stıl duruma gelirler.
                last_expired_at = datetime.now() if len(jwk_list) == 0 else jwk_list[0].expired_at
                expired_at = last_expired_at + timedelta(days=JWKS_ROTATION)
                jwk_list.insert(0, await self.create_jwk(expired_at))
        return jwk_list

    async def create_jwk(self, expired_at: datetime) -> JwkModel:
        """Yeni bir jWK verisi oluşturur"""

        # Private Key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Public Key
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        jwk = JWK.from_pem(public_pem)
        jwk_dict = {
            **jwk.export(as_dict=True), # type: ignore
            "alg": "RS256",
            "use": "sig"
        }

        return await self.create(CreateJwkModel(
            key_id=jwk_dict.get("kid"), # type: ignore
            private_pem=private_pem.decode("utf-8"),
            public_pem=public_pem.decode('utf-8'),
            jwk=jwk_dict,
            expired_at=expired_at
        ))
