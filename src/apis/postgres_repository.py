from contextlib import closing, contextmanager
from collections.abc import Generator

from psycopg2.extensions import cursor

from src.apis.app_logger import AppLogger
from src.apis.postgres_connection import PostgresConnection


class PostgresRepository:
    def __init__(self, connection: PostgresConnection):
        self._connection = connection
        self._logger = AppLogger(self.__class__.__name__)

    @contextmanager
    def cursor(self, name: str = "postgres_cursor") -> Generator[cursor, None, None]:
        with closing(self._connection.connect()) as connection:
            with connection.cursor(name=name) as cur:
                yield cur