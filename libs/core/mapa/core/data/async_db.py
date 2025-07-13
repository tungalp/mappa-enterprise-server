from contextlib import asynccontextmanager
from typing import Callable
import logging
from asyncio import current_task
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker, async_scoped_session
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)


class AsyncDatabase:
    """Asenkron Veritabanı Sınıfı"""

    def __init__(self, db_url: str) -> None:
        env = os.environ.get("MAPA_ENV")
        echo = False
        if env == "DEVELOPMENT":
            echo = True
        self.engine = create_async_engine(
            db_url,
            echo=echo,
            pool_pre_ping=True,
            pool_size=15,
            max_overflow=10,
            pool_recycle=3600,  # 1 saat sonra bağlantıları yenile
            pool_timeout=30,  # Havuz doluysa 30 saniye bekle
        )
        self._async_session_factory = async_scoped_session(
            async_sessionmaker(
                bind=self.engine, expire_on_commit=False, class_=AsyncSession
            ),
            scopefunc=current_task,
        )

    @asynccontextmanager
    async def session(self) -> Callable[..., AsyncSession]:
        """Yeni bir asenkron veritabanı oturumu oluşturur."""
        async_session: AsyncSession = self._async_session_factory()
        try:
            yield async_session
        except Exception as e:
            logger.exception("Session rollback because of exception")
            await async_session.rollback()
            raise
        finally:
            await async_session.close()
