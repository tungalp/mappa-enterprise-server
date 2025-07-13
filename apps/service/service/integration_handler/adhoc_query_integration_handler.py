from functools import lru_cache
import json
from typing import Any, Dict, List
from pydantic import TypeAdapter
from sqlalchemy import text
from sqlalchemy.engine import URL
from mapa.core.data.async_db import AsyncDatabase
from mapa.core.data.db import Database
from mapa.core.data.query_args import QueryArgs
from mapa.gateway.connection_info.database_info_model import DatabaseInfo
from mapa.gateway.integration.integration_model import AdHocQueryConnection
from mapa.gateway.constant import MethodTypes, SqlResultTypes
from service.integration_handler.integration_handler import IntegrationHandler
from service.integration_handler.table_repository import TableDesc, TableRepository
from service.model.request import ServiceRequest
from service.model.response import ServiceResponse
from oracledb.dsn import makedsn


def create_db_engine(db_url: str, is_async: bool) -> AsyncDatabase | Database:
    """Verilen bağlantı parametrelerine göre veritabanı bağlantısı oluşturur."""
    return AsyncDatabase(db_url) if is_async else Database(db_url)


class AdHocQueryIntegrationHandler(IntegrationHandler):
    """Http İsteklerini karşılayan entegrasyon sınıfı"""

    dialect_driver_mapping = {
        "postgresql": "psycopg2",
        "oracle": "cx_oracle",
        "mssql": "pyodbc",
    }

    async def execute(self, service_request: ServiceRequest) -> ServiceResponse:
        if not self.integration.connection_info:
            raise ValueError("ConnectionInfo not defined")
        # Veritabanı oluşturulur
        db_conn = self._create_db(self.integration.connection_info.params)
        query_conn = AdHocQueryConnection(**(self.integration.connection))

        if self._check_sql_is_table(query_conn.sql):
            body = await self._execute_table(db_conn, query_conn, service_request)
        else:
            body = await self._execute_sub_query(db_conn, query_conn, service_request)
 
        # Servis dönüş değeri oluşturulur.
        response = ServiceResponse(
            status_code=200,
            response_type="application/json",
            body=dict(body)
        )
        return response

    async def _execute_table(self,
                             db_conn: AsyncDatabase | Database,
                             adhoc_conn: AdHocQueryConnection,
                             service_request: ServiceRequest):
        # Post metodu dışındaki metodlar query parametresini kullanılır.
        params = {**service_request.path_params,
                  **service_request.query_params}
        query = params.get("query", None)
        if not query is None:
            # Gelen json ifadesi QueryArgs a dönüştürülür.
            params["query"] = TypeAdapter(
                QueryArgs).validate_python(json.loads(query))

        table_desc = TableDesc(adhoc_conn.sql, adhoc_conn.parent_column)

        ret_val = {}
        match service_request.method:
            case MethodTypes.GET:
                ret_val = await self.__execute_table_get(db_conn, table_desc, params)
            case MethodTypes.POST:
                ret_val = await self.__execute_table_post(db_conn, table_desc, params, service_request.body)
            case MethodTypes.PUT:
                ret_val = await self.__execute_table_put(db_conn, table_desc, params, service_request.body)
            case MethodTypes.DELETE:
                ret_val = await self.__execute_table_delete(db_conn, table_desc, params)
        return ret_val

    async def _execute_sub_query(self, db_conn: AsyncDatabase | Database, adhoc_conn: AdHocQueryConnection, service_request: ServiceRequest):
        params = {**service_request.path_params,
                  **service_request.query_params}
        body = service_request.body
        if isinstance(body, Dict):
            params = {**params, **body}
        elif isinstance(body, List):
            body_list: List[Any] = list(body)
            #TODO: Test kodlarıyla in, ilike, like vb. operatorler test edilmeli. (11.07.2024)
            params = [{**params, **body_item} for body_item in body_list]
        # Veri sorgulanır.
        if isinstance(db_conn, AsyncDatabase):
            async with db_conn.session() as async_session:
                stmt = text(adhoc_conn.sql)
                result = await async_session.execute(stmt, params)
                data = [dict(row) for row in result.mappings()
                        ] if result.returns_rows else []
                row_count = result.rowcount
                await async_session.commit()
        else:
            with db_conn.session() as session:
                stmt = text(adhoc_conn.sql)
                result = session.execute(stmt, params)
                data = [dict(row) for row in result.mappings()
                        ] if result.returns_rows else []
                row_count = result.rowcount
                session.commit()

        body = {
            "affected": row_count
        }
        match adhoc_conn.result_type:
            case SqlResultTypes.MULTI:
                body["data"] = [dict(item)
                                for item in data][:adhoc_conn.max_count]
            case SqlResultTypes.SINGLE:
                body["data"] = dict(data[0]) if len(data) > 0 else {}
            case _:
                body["data"] = None
        return body

    def _check_sql_is_table(self, sql: str) -> bool:
        # Sql cümlesinde sadece tablo ve şema adı olup olmadığını kontrol eder.
        parts = sql.strip().split(" ")
        return len(parts) == 1

    def _split_table_name(self, full_name: str) -> Dict[str, str]:
        parts = full_name.strip().split(".")
        return {
            "schema": "" if len(parts) == 1 else parts[0],
            "table": parts[-1]
        }

    def _create_db(self, params: Dict[str, Any]) -> AsyncDatabase | Database:
        db_info = DatabaseInfo(**params)
        driver = self.dialect_driver_mapping.get(db_info.dialect)
        driver_expr = f"{db_info.dialect}{'+' + driver if driver else ''}"
        db_url = URL.create(
            drivername=driver_expr,
            username=db_info.username,
            password=db_info.password,
            host=db_info.host,
            port=db_info.port,
            database=db_info.database
        )

        # `is_async` kontrolü veritabanı türüne göre belirleniyor
        is_async = False
        if db_info.dialect.find("oracle") > -1:
            dsn = makedsn(
                host=db_info.host,
                port=db_info.port or 1521,
                service_name=db_info.database
            )
            db_url = f"{driver_expr}://{db_info.username}:{db_info.password}@{dsn}"
        elif db_info.dialect.find("mssql") > -1:
            db_url = f"{driver_expr}://{db_info.username}:{db_info.password}@{db_info.host}:{db_info.port}/{db_info.database}?TrustServerCertificate=yes&driver=ODBC+Driver+18+for+SQL+Server"
        elif db_info.dialect.find("postgres") > -1:
            is_async = False
            
        return create_db_engine(db_url, is_async=is_async)

    async def __execute_table_get(self, db_conn: AsyncDatabase | Database, table_desc: TableDesc, params: Dict[str, Any]):
        repo = TableRepository(db_conn, table_desc)

        # Sorgu parametreleri alınır
        query_args: QueryArgs = params["query"]
        if query_args is None:
            raise ValueError("QueryArgs can not be none in get request")
        result = repo.paging(query_args)

        return result

    async def __execute_table_post(self,
                                   db_conn: AsyncDatabase | Database,
                                   table_desc: TableDesc,
                                   params: Dict[str, Any],
                                   body: Any):

        repo = TableRepository(db_conn, table_desc)
        if isinstance(body, Dict):
            values = {**body}
        elif isinstance(body, List):
            body_list: List[Any] = list(body)
            values = [{**body_item} for body_item in body_list]
        else:
            values = params

        result = repo.create(values)
        return result

    async def __execute_table_put(self,
                                  db_conn: AsyncDatabase | Database,
                                  table_desc: TableDesc,
                                  params: Dict[str, Any],
                                  body: Any):
        # Repository
        repo = TableRepository(db_conn, table_desc)

        # Gelen veri düzenlenir.
        if isinstance(body, Dict):
            values = {**body}
        elif isinstance(body, List):
            body_list: List[Any] = list(body)
            values = [{**body_item} for body_item in body_list]
        else:
            raise ValueError("Wrong body format", body)

        # Sorgu parametreleri alınır
        query_args: QueryArgs = params.get("query", None)

        if not query_args is None and isinstance(values, Dict):
            result = repo.update_with_query(query_args, values)
        elif query_args is None:
            result = repo.update(values)
        else:
            raise ValueError("Wrong update parameters", params, body)

        return result

    async def __execute_table_delete(self,
                                     db_conn: AsyncDatabase | Database,
                                     table_desc: TableDesc,
                                     params: Dict[str, Any]):
        # Repository
        repo = TableRepository(db_conn, table_desc)

        # Sorgu parametreleri alınır
        query_args: QueryArgs = params.get("query", None)
        if query_args is None:
            raise ValueError("QueryArgs can not be none in delete request")

        return repo.delete(query_args)
