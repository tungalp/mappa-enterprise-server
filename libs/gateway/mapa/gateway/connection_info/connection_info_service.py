from typing import Any, Dict, List
from mapa.core.data.result import PagingResult
from mapa.gateway.connection_info.authentication_info_model import AuthenticationInfo, BasicAuthAuthenticationInfo
from mapa.gateway.constant import AuthenticationInfoTypes, ConnectionInfoTypes
from oracledb.dsn import makedsn

from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import URL
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.query_args import Filter, FilterOp, QueryArgs
from mapa.core.data.base_entity_service import BaseEntityService
from mapa.gateway.connection_info.connection_info_model import CreateConnectionInfo, UpdateAllConnectionInfo, UpdateConnectionInfo, ConnectionInfo
from mapa.gateway.connection_info.connection_info_repository import ConnectionInfoRepository
from mapa.gateway.connection_info.database_info_model import DatabaseInfo


class ConnectionInfoService(BaseEntityService[ConnectionInfoRepository, ConnectionInfo, CreateConnectionInfo, UpdateConnectionInfo, UpdateAllConnectionInfo]):
    """ConnectionInfo Servisi"""

    dialect_driver_mapping = {
        "postgresql": "psycopg2",
        "oracle": "oracledb",
        "mssql": "pyodbc",
    }

    def __init__(self, async_db: AsyncDatabase) -> None:
        super().__init__(async_db, ConnectionInfoRepository, ConnectionInfo)

    async def get(self, obj_id: Any, tenant_id: str | None = None, field_list: List[str | Dict[str, Any]] | None = None, hiddenPassword:bool | None = None) -> ConnectionInfo:
        result = await super().get(obj_id, tenant_id)
        if hiddenPassword:
            result = self._hiddenPassword(result)
        return result  
        
    async def paging(self, query_args: QueryArgs, tenant_id: str | None = None, hiddenPassword:bool | None = None) -> PagingResult[ConnectionInfo]:
        result = await super().paging(query_args, tenant_id)
        if hiddenPassword:
            for item in result.items:
                item = self._hiddenPassword(item)
        return result
    
  
    async def find_one(self, query_args: QueryArgs, tenant_id: str | None = None, hiddenPassword:bool | None = None) -> ConnectionInfo | None:
        result = await super().find_one(query_args, tenant_id)
        if result and hiddenPassword:
            result = self._hiddenPassword(result)
        return result  
  
    async def find(self, query_args: QueryArgs , tenant_id: str | None = None , hiddenPassword:bool | None = None) -> List[ConnectionInfo]:
        result = await super().find(query_args, tenant_id)
        if hiddenPassword:
            for item in result:
                item = self._hiddenPassword(item)
        return result  
    
    # Gelen connection_info ID listesine göre bağlantı kontrolunu test eder. (04.03.2024)
    async def isConnectList(self, connection_info_ids: List[str], tenant_id: str | None = None) -> List[ConnectionInfo]:
        connection_info_list = []
        query_args = QueryArgs(where=[
            Filter(field="id", op=FilterOp.IN, value=[str(item) for item in connection_info_ids])])

        connection_info_list: List[ConnectionInfo] = await super().find(query_args, tenant_id)
        for item in connection_info_list:
            item.params["is_success"] = self._isConnect(item.params)
        return connection_info_list


    # Gelen connection_info bilgisine göre bağlantı kontrolunu test eder. (04.03.2024)
    async def isConnect(self, connection_info: CreateConnectionInfo, tenant_id: str | None = None) -> CreateConnectionInfo:

        connection_info.params["is_success"] = self._isConnect(
            connection_info.params)

        return connection_info

    # Verilen Db parametrelerine göre bağlantı kontrolunu test eder. (04.03.2024)
    def _isConnect(self, params: Dict[str, str]) -> bool:

        ret_val = False
        db_info = DatabaseInfo(**params)  # type: ignore     
        driver = self.dialect_driver_mapping.get(db_info.dialect)
        driver_expr = f"{db_info.dialect}{'+' + driver if driver else ''}"

        db_url = URL.create(
            drivername=driver_expr,
            username=db_info.username,
            password=db_info.password,
            host=db_info.host,
            port=db_info.port,
            database=db_info.database)

        if db_info.dialect.find("oracle") > -1:
            dsn = makedsn(host=db_info.host, port=db_info.port or 1521,
                          service_name=db_info.database)
            db_url = f"{driver_expr}://{db_info.username}:{db_info.password}@{dsn}"
            is_async = False
        elif db_info.dialect.find("mssql") > -1:
            db_url = f"{driver_expr}://{db_info.username}:{db_info.password}@{db_info.host}:{db_info.port}/{db_info.database}?TrustServerCertificate=yes&driver=ODBC+Driver+18+for+SQL+Server"

        engine = create_engine(db_url, echo=True, connect_args={'connect_timeout': 2}) # second
        try:
            conn = engine.connect()
            conn.close()
            ret_val = True
        except Exception as ex:
            ret_val = False

        return ret_val
    
    
    # Gelen connection_info bilgisinin password prop bilgisini dışarıya bildirmemek için gizlenmiştir.. (04.03.2024)
    def _hiddenPassword(self, connection_info:ConnectionInfo) -> ConnectionInfo:
        if connection_info.type == ConnectionInfoTypes.DATABASE:
            connection_info.params["password"] = ""
        elif connection_info.type == ConnectionInfoTypes.AUTHENTICATION:
            auth_info = AuthenticationInfo(**connection_info.params)
            if auth_info.type == AuthenticationInfoTypes.BASICAUTH:
                connection_info.params["auth_params"]["password"] = ""
                
        return connection_info