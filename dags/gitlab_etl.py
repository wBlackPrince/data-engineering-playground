import json
import logging
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



logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(name)s:%(message)s',
    datefmt='%d.%m.%Y %H:%M:%S'
)
logger = logging.getLogger(__name__)


@dag(
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=["example"],
)
def gitlab_etl():

    @task()
    async def extract():
        logger.info("Начало извлечения данных...")

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

        response: Result[Response] = await gitlab_client.get_commits_async(75591172)

        if is_failure(response):
            AppLogger.log_error(f"message: {response.message}, code: {response.code}, details: {response.details}")

        
        data = response.value.content

        try:
            commit_data_dict: list[dict] = json.loads(data)
        except:
            logger.exception("Ошибка при десериализации json")
            raise
        return commit_data_dict

    
    @task()
    def transform_and_load(commit_data_dict: list[dict]):
        logger.info("Начало трансформации данных...")

        commits: list[GitlabCommit] = []
        
        for commit_data in commit_data_dict:
            commits.append(GitlabCommit.from_dict(commit_data))
        
        batch: list[tuple] = [commit.to_tuple() for commit in commits]


        logger.info("Начало загрузки данных в ClickHouse...")

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
            logger.exception("Ошибка при загрузке в ClickHouse")
            raise



    commits_data = extract()
    transform_and_load(commits_data)


gitlab_etl()
