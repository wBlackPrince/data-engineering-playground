import json
import logging
import pendulum

from airflow.sdk import dag, task
from clickhouse_driver import Client

from apis.async_http_client import AsyncHttpClient
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
    def extract():
        logger.info("Начало извлечения данных...")
        data_string: str = AsyncHttpClient.get_commit_from_gitlab_api()
        try:
            commit_data_dict: list[dict] = json.loads(data_string)
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
