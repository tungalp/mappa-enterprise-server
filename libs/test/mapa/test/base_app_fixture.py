import json
import pathlib
import time
import jwt
from typing import Any, Dict, List
from pathlib import Path
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from sqlalchemy import MetaData, Table, create_engine, insert, text
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity import Base
from jwcrypto.jwk import JWK
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from mapa.test.base_fixture import BaseFixture


class BaseAppFixture(BaseFixture):
    """Tüm Application Fikstür sınıfılarının üst sınıfı"""

    private_key: str = ""
    public_key: str = ""

    def __init__(self) -> None:
        self.app = None
        super().__init__()

    @property
    def app(self):
        return self._app

    @app.setter 
    def app(self, value):
        self._app = value

    def drop_schema_and_migration_table(self, schema: str, enum_types: List[str] = None):
        """Test veritabanını oluşturur."""
        try:
            # Use sync engine for table creation to ensure events are triggered
            sync_engine = create_engine(self.db_url_init)
            with sync_engine.begin() as conn:
                # Drop schema-specific enum types first (they persist at database level)
                if enum_types:
                    for enum_type in enum_types:
                        conn.execute(text(f"drop type if exists {enum_type} cascade"))
                    
                # Drop schema if it exists
                conn.execute(text(f"drop schema if exists {schema} cascade"))
                # Drop migration table for the schema
                conn.execute(text(f"drop table if exists alembic_version_{schema}"))
            sync_engine.dispose()
        except Exception as ex:
            print(ex)
            raise

        return True

    def create_access_token(self, user_id: UUID, tenant_id: UUID,
                            client_id: str, audience: str,
                            api_scopes: List[str],
                            lifetime: int = 60 * 60 * 24 * 360) -> str:
        """AccessToken"""
        scope = "openid email profile"
        now = datetime.now()
        payload = {
            "iss": self.issuer,
            "sub": str(user_id),
            "aud": audience,
            "iat": now.timestamp(),
            "nbf": (now - timedelta(seconds=1)).timestamp(),
            "exp": (now + timedelta(seconds=lifetime)).timestamp(),
            "azp": client_id,
            "jti": str(uuid4()),
            "tenant_id": str(tenant_id),
            "scope": scope,
            "api_scopes": api_scopes
        }
        jwks = JWK.from_pem(self.public_key.encode("latin-1"))
        jwt_token = jwt.encode(payload, self.private_key, algorithm='RS256', headers={
            "kid": jwks.get("kid")
        })
        time.sleep(1)
        return jwt_token

    def decode_token(self, token: str) -> Dict[str, Any]:
        options = {
            "verify_aud": False,
            "verify_iat": False
        }
        return jwt.decode(
            token, self.public_key, algorithms=["RS256"], options=options, issuer=self.issuer)

    def init_keys(self):
        # Veritabanı kayıtları oluşturulur.
        db = self.create_db_instance_sync(self.db_url_init)
        jwk_table = Table("jwk", MetaData(),autoload_with=db.engine, schema="sso")
        now = datetime.now()
        value_list = [
            self._create_jwk_model(now + timedelta(days=20)),
            self._create_jwk_model(now + timedelta(days=10)),
        ]
        with db.session() as session:
            stmt = insert(jwk_table)
            result = session.execute(stmt, value_list)
            session.commit()

        self.private_key = str(value_list[0].get("private_pem"))
        self.public_key = str(value_list[0].get("public_pem"))

        jwks_json = {
            "keys": [jwk_model.get("jwk") for jwk_model in value_list]
        }
        jwks_json_path = pathlib.Path.home().joinpath("./jwks.json")
        with open(jwks_json_path, "w") as f:
            f.write(json.dumps(jwks_json))
        
        for middleware in self.app.user_middleware:
            if middleware.cls.__name__ == "AuthenticationMiddleware":
                middleware.kwargs["backend"].jwks_uri = self.jwks_json_uri
            
    @property
    def jwks_json_uri(self):
        return "file://" + str(pathlib.Path.home().joinpath("./jwks.json"))

    def _create_jwk_model(self, expired_at: datetime) -> Dict[str, Any]:
        private_key, private_pem = self._create_private_key()
        public_key, public_pem = self._create_public_key(private_key)
        jwk = JWK.from_pem(public_pem)
        jwk_dict = {
            **jwk.export(as_dict=True),  # type: ignore
            "alg": "RS256",
            "use": "sig"
        }
        return {
            "id": str(uuid4()),
            "key_id": jwk_dict.get("kid"),  # type: ignore
            "private_pem": private_pem.decode("utf-8"),
            "public_pem": public_pem.decode('utf-8'),
            "jwk": jwk_dict,
            "expired_at": expired_at,
            "created_at": datetime.now()
        }

    def _create_private_key(self):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return private_key, private_pem

    def _create_public_key(self, private_key):
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return public_key, public_pem
