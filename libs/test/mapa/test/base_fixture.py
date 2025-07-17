from typing import Any, List
from sqlalchemy import text, create_engine
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.base_entity import Base

from mapa.core.data.db import Database

class BaseFixture:
    """Tüm Fikstür sınıfılarının üst sınıfı"""

    db_url_init = "postgresql://postgres:postgres@postgres/mapa_test"
    db_url = "postgresql://mapa:12345Abc.@postgres/mapa_test"

    db_url_async_init = "postgresql+asyncpg://postgres:postgres@postgres/mapa_test"
    db_url_async = "postgresql+asyncpg://mapa:12345Abc.@postgres/mapa_test"

    tenant_id = "10a2238f-4d1e-4626-9f3c-799d3ef5e96d"
    issuer = "http://localhost:33000"
    
    def __init__(self) -> None:
        pass

    def create_db_instance(self, db_url: str) -> AsyncDatabase:
        """Create  Database"""
        return AsyncDatabase(db_url)

    def create_db_instance_sync(self, db_url: str) -> Database:
        """Create  Database"""
        return Database(db_url)
    
    async def create_schema(self,  async_db: AsyncDatabase, schema_name: str):
        """Create schema"""
        try:
            async with async_db.engine.begin() as conn:
                await conn.execute(text(f"create schema if not exists {schema_name}"))
        except Exception as ex:
            print(ex)
            raise ex

    async def create_database(self, async_db: AsyncDatabase) -> bool:
        """Veritabanındaki tabloları siler ve yeniden oluşturur."""
        try:
            # Use sync engine for table creation to ensure events are triggered
            sync_engine = create_engine(self.db_url_init)
            with sync_engine.begin() as conn:
                # Drop existing tables
                for tbl in reversed(Base.metadata.sorted_tables):
                    conn.execute(text(f"drop table if exists {tbl.fullname} cascade"))
                # Create tables - this will trigger the after_create event
                Base.metadata.create_all(conn)
            sync_engine.dispose()
        except Exception as ex:
            print(ex)
            raise

        return True

    async def create_data(self, async_db: AsyncDatabase, instances: List[Any]) -> bool:
        """Veritabanında tabloları ve örnek verileri oluşturur."""

        async with async_db.session() as session:
            # Set the tenant_id session variable for RLS
            await session.execute(text(f"SET app.tenant_id = '{self.tenant_id}'"))
            session.add_all(instances)
            await session.commit()

        return True

    async def grant_permissions(self, async_db: AsyncDatabase, db_name: str, user: str, schema: str = "public"):
        """Kullanıcıya veritabanıda gerekli olan yetkileri tanımlar"""

        async with async_db.session() as session:
            await session.execute(
                text(f"GRANT connect ON DATABASE {db_name} TO {user}")
            )
            await session.execute(
                text(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {user}")
            )
            await session.execute(
                text(f"GRANT USAGE ON SCHEMA {schema} TO {user}")
            )
            await session.execute(
                text(f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA {schema} TO {user}")
            )
            await session.execute(
                text(f"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA {schema} TO {user}")
            )
            await session.execute(
                text(f"GRANT pg_read_all_data TO {user}")
            )
            await session.execute(
                text(f"GRANT pg_write_all_data TO {user}")
            )
            await session.execute(
                text(f"ALTER DEFAULT PRIVILEGES FOR ROLE {user} IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {user}")
            )

            await session.commit()
