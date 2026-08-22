import json
import os
from httpx import Response
import pendulum

from airflow.sdk import dag, task
from clickhouse_driver import Client

from apis.app_logger import AppLogger
from apis.async_http_client import AsyncHttpClient
from apis.gitlab_client import GitlabClient
from apis.result import Result, is_failure
from models.gitlab_commit import GitlabCommit



@dag(
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=["example"],
)
def gitlab_etl():
    logger = AppLogger("GITLAB_ETL")

    @task()
    async def extract():
        logger.log_info("Начало извлечения данных...")

        token = os.getenv("GITLAB_API_TOKEN")
        if token is None:
            raise RuntimeError("GITLAB_API_TOKEN is not set")
        
        http_client = AsyncHttpClient(
            base_url="https://gitlab.com/api/v4", 
            headers={
                "PRIVATE-TOKEN": token,
            }
        )

        gitlab_client = GitlabClient(http_client)

        logger.log_info("Начало сбора и трансформации данных...")

        response: Result[list[GitlabCommit]] = await gitlab_client.get_commits_async(75591172)

        if is_failure(response):
            logger.log_error(response)
            raise
        
        batch: list[tuple] = [commit.to_tuple() for commit in response]

        logger.log_info("Начало загрузки данных в ClickHouse...")

        client = Client(
            host="clickhouse",
            port=9000,
            database="warehouse",
            user="student",
            password="strongpassword",
        )

        try:
            client.execute(f'INSERT INTO {GitlabCommit.PATH_TO_TABLE} ({GitlabCommit.columns()}) VALUES', batch)
        except Exception as ex:
            logger.log_exception("Ошибка при загрузке в ClickHouse", ex)
            raise



    commits_data = extract()
    transform_and_load(commits_data)


gitlab_etl()
