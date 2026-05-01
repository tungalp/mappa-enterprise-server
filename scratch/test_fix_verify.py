import sys
import unittest
from unittest.mock import MagicMock, AsyncMock, patch
import asyncio
from sqlalchemy import select, text, Column, Integer, String
from sqlalchemy.orm import declarative_base
from mapa.core.data.base_repository import BaseRepository
from mapa.core.data.query_args import QueryArgs, Filter, FilterOp
from pydantic import BaseModel

Base = declarative_base()

class MockEntity(Base):
    __tablename__ = "mock"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    tenant_id = Column(String)

# Mock Database
class MockDB:
    def session(self):
        session = AsyncMock()
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        return session

class TestBaseRepository(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.db = MockDB()
        self.repo = BaseRepository(self.db, MockEntity)

    async def test_set_tenant_id_safe(self):
        session = AsyncMock()
        tenant_id = "123-uuid"
        await self.repo._BaseRepository__set_tenant_id(session, tenant_id)
        
        call_args = session.execute.call_args
        stmt = call_args[0][0]
        self.assertIn("set app.tenant_id=:t_id", str(stmt))
        self.assertEqual(stmt._bindparams['t_id'].value, "123-uuid")

    async def test_apply_filter_contains(self):
        with patch.object(self.repo, '_BaseRepository__create_field_list', return_value=["name"]), \
             patch.object(self.repo, '_BaseRepository__create_expand_list', return_value=[]), \
             patch.object(self.repo, '_BaseRepository__find_relations', return_value=({}, [])), \
             patch.object(self.repo, '_BaseRepository__cast_field_value', side_effect=lambda attr, val: val):
            
            query_args = QueryArgs(where=[Filter(field="name", op=FilterOp.CONTAINS, value="adm")])
            stmt = select(MockEntity)
            stmt = self.repo._BaseRepository__apply_query_args(stmt, query_args)
            
            # Check if stmt has the correct filter
            # The filter should be MockEntity.name.contains('adm')
            self.assertIn("mock.name LIKE '%%' || :name_1 || '%%'", str(stmt))

if __name__ == "__main__":
    unittest.main()
