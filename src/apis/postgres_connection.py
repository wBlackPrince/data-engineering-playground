from __future__ import annotations

from dataclasses import dataclass

from mypy.errorcodes import ErrorCode
import psycopg2

from src.apis.result import FailureContext, Result, failure, success

@dataclass(frozen=True, slots=True)
class PostgresConnection:
    host: str
    port: int
    database: str
    user: str
    password: str

    @staticmethod
    def from_connection_string(
        connection_string: str | None,
    ) -> Result[PostgresConnection]:
        context = FailureContext(
            operation="from_connection_string",
            source="PostgresConnection",
        )

        if not connection_string or not connection_string.strip():
            return failure(
                message="PostgreSQL connection string was not provided",
                code=ErrorCode.UNKNOWN,
                context=context,
            )

        try:
            parameters = {
                key.lower(): value
                for parameter in connection_string.split()
                for key, value in [parameter.split("=", 1)]
            }

            required_parameters = {"host", "dbname", "user", "password"}
            missing_parameters = required_parameters - parameters.keys()

            if missing_parameters:
                return failure(
                    message="Missing required PostgreSQL connection parameters",
                    code=ErrorCode.UNKNOWN,
                    context=context,
                    details={"missing_parameters": sorted(missing_parameters)},
                )

            connection = PostgresConnection(
                host=parameters["host"],
                port=int(parameters.get("port", 5432)),
                database=parameters["dbname"],
                user=parameters["user"],
                password=parameters["password"],
            )

            return success(connection)

        except (ValueError, TypeError) as exc:
            return failure(
                message="Invalid PostgreSQL connection string",
                code=ErrorCode.UNKNOWN,
                context=context,
                details={
                    "exception": type(exc).__name__,
                    "detail": str(exc),
                },
            )

    def connect(self) -> psycopg2.extensions.connection:
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.database,
            user=self.user,
            password=self.password,
        )