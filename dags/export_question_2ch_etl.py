
import logging
import os
from contextlib import closing
from typing import Any

import pendulum
import psycopg2

from airflow.sdk import dag, task

from src.apis.clickhouse_repository import ClickHouseRepository
from src.models.question import Question
from src.apis.error_code import ErrorCode
from src.apis.result import (
    FailureContext,
    Result,
    UnitResult,
    is_failure,
)

logger = logging.getLogger(__name__)


@dag(
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=["export", "postgres", "clickhouse"],
)
def export_question_2ch_etl():

    @task()
    def etl() -> None:
        context = FailureContext(
            operation="export_question_2ch_etl",
            source="etl"
        )

        logger.info("Начало извлечения данных из PostgreSQL...")

        pg_connection_string = os.getenv("CONNECTIONSTRINGS__POSTGRES")

        if not pg_connection_string:
            raise RuntimeError(
                "CONNECTIONSTRINGS__POSTGRES is not set"
            )

        repository = ClickHouseRepository()
        batch_size = 1000
        total_count = 0

        with closing(
            psycopg2.connect(pg_connection_string)
        ) as pg_conn:

            with pg_conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        inet_server_addr(),
                        inet_server_port(),
                        current_database(),
                        to_regclass('public.questions'),
                        to_regclass('questions')
                """)

                logger.info("PostgreSQL diagnostic: %s", cur.fetchone())

                cur.execute("""
                    SELECT
                        id,
                        description,
                        "Type",
                        points_cost,
                        test_id,
                        position_index,
                        match_ids,
                        option_ids,
                        right_answer
                    FROM public.questions
                """)

                while True:
                    rows: list[tuple[Any, ...]] = cur.fetchmany(batch_size)

                    if not rows:
                        break

                    questions: list[Question] = []

                    for row in rows:
                        question_result: Result[Question] = (
                            Question.from_tuple(row)
                        )

                        if is_failure(question_result):
                            raise RuntimeError(
                                f"Failed to create Question: "
                                f"{question_result.message}. "
                                f"Details: {question_result.details}"
                            )

                        questions.append(question_result.value)

                    batch: list[tuple] = [
                        question.to_tuple()
                        for question in questions
                    ]

                    logger.info(
                        "Загрузка батча в ClickHouse. Размер: %s",
                        len(batch),
                    )

                    insert_result: UnitResult = (
                        repository.insert_query(Question, batch)
                    )

                    if is_failure(insert_result):
                        logger.error(insert_result)
                        raise RuntimeError(insert_result.message)

                    total_count += len(batch)

        logger.info(
            "ETL завершён. Всего обработано записей: %s",
            total_count,
        )

    etl()


export_question_2ch_etl()
