from mapa.core.data.base_service import BaseService
from mapa.core.data.async_db import AsyncDatabase


class BaseDbService(BaseService):
    """Direk olarak veritabanını kullanan servislerin üst sınıfıdır
    Herhangi bir entity sınıfına bağlı kalmadan standart dışı metodlar geliştirmek 
    için kullanılır
    """
    
    async_db: AsyncDatabase
    
    def __init__(self, async_db: AsyncDatabase) -> None:
        self.async_db = async_db
        super().__init__()