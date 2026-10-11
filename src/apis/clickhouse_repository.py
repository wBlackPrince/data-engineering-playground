from clickhouse_driver import Client

from src.apis.app_logger import AppLogger
from src.apis.error_code import ErrorCode
from src.apis.result import FailureContext, UnitResult, failure, unit_success
from src.models.entity import Entity


class ClickHouseRepository:
    def __init__(self):
        self._client = Client(
            host="clickhouse",
            port=9000,
            database="warehouse",
            user="student",
            password="strongpassword",
        )
        self._logger = AppLogger(self.__class__.__name__)

    def insert_query(self, cls: type[Entity], batch: list[tuple]) -> UnitResult:
        try:
            self._client.execute(f'INSERT INTO {cls.PATH_TO_TABLE} ({cls.columns()})', batch)
            return unit_success("Success insert to CH!")
        except Exception as ex:
            result = failure(
                message="Ошибка при загрузке в ClickHouse",
                code=ErrorCode.CLICKHOUSE_INSERT_ERROR,
                context=FailureContext(
                    operation="insert_query",
                    source=self.__class__.__name__,
                ),
                details={
                    "exception": type(ex).__name__,
                    "detail": str(ex),
                },
            )

            return result

    