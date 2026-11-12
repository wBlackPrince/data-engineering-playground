from __future__ import annotations

from dataclasses import dataclass

from clickhouse_driver import Client
from pluggy import Result

from src.apis.error_code import ErrorCode
from src.apis.result import FailureContext, failure, success


@dataclass(frozen=True, slots=True)
class ClickHouseConnection:
    host: str
    port: int
    database: str
    user: str
    password: str

    @staticmethod
    def from_connection_string(connection_string: str) -> Result[ClickHouseConnection]:
        context = FailureContext(
            operation="from_connection_string",
            source="ClickHouseConnection",
        )

        if not connection_string or not connection_string.strip():
            return failure(
                message="ClickHouse connection string was not provided",
                code=ErrorCode.UNKNOWN,
                context=context,
            )
        
        try:
            parameters = {}

            for part in connection_string.split(";"):
                if not part.strip():
                    continue

                key, value = part.split("=", 1)
                parameters[key.strip().lower()] = value.strip()

            required_parameters = {"host", "user", "password"}
            missing_parameters = required_parameters - parameters.keys()

            if missing_parameters:
                return failure(
                    message="Missing required ClickHouse connection parameters",
                    code=ErrorCode.UNKNOWN,
                    context=context,
                    details={"missing_parameters": sorted(missing_parameters)},
                )

            connection = ClickHouseConnection(
                host=parameters["host"],
                port=int(parameters.get("port", 9000)),
                database=parameters.get("database", "warehouse"),
                user=parameters["user"],
                password=parameters["password"],
            )

            return success(connection)

        except (ValueError, TypeError) as exc:
            return failure(
                message="Invalid ClickHouse connection string",
                code=ErrorCode.UNKNOWN,
                context=context,
                details={
                    "exception": type(exc).__name__,
                    "detail": str(exc),
                },
            )

    def connect(self) -> Client:
        return Client(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password,
        )