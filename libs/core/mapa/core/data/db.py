from contextlib import contextmanager, AbstractContextManager
from typing import Callable
import logging
import os
from sqlalchemy import create_engine, orm
from sqlalchemy.orm import Session
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)


class Database:
    """Senkron Veritabanı Sınıfı"""

    def __init__(self, db_url: str) -> None:
        env = os.environ.get("MAPA_ENV")
        echo = False
        if env == "DEVELOPMENT":
            echo = True
        self.engine = create_engine(
            db_url,
            echo=echo,
            pool_pre_ping=True,
            pool_size=15,
            max_overflow=10,
            pool_recycle=3600,  # 1 saat sonra bağlantıları yenile
            pool_timeout=30,  # Havuz doluysa 30 saniye bekle
        )
        self._session_factory = orm.sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )

    @contextmanager
    def session(self) -> Callable[..., AbstractContextManager[Session]]:
        """Yeni bir veritabanı oturumu oluşturur."""
        session: Session = self._session_factory()
        try:
            yield session
        except Exception:
            logger.exception("Session rollback because of exception")
            session.rollback()
            raise
        finally:
            session.close()
