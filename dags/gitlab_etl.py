import os
import pendulum

from airflow.sdk import dag, task

from src.apis.app_logger import AppLogger
from src.apis.async_http_client import AsyncHttpClient
from src.apis.clickhouse_repository import ClickHouseRepository
from src.apis.gitlab_client import GitlabClient
from src.apis.result import Result, UnitResult, is_failure
from src.models.gitlab_commit import GitlabCommit



@dag(
    schedule=None,
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    tags=["example"],
)
def gitlab_etl():
    logger = AppLogger("GITLAB_ETL")\

    @task()
    async def gitlab_etl() -> list[GitlabCommit]:
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

        response_result: Result[list[GitlabCommit]] = await gitlab_client.get_commits_async(75591172)

        if is_failure(response_result):
            logger.log_error(response_result)
            raise RuntimeError(response_result.message)

        commit_list: list[GitlabCommit] = response_result.value

        batch: list[tuple] = [commit.to_tuple() for commit in commit_list]

        logger.log_info("Начало загрузки данных в ClickHouse...")
                
        repository = ClickHouseRepository()

        insert_result: UnitResult = repository.insert_query(GitlabCommit, batch)

        if is_failure(insert_result):
            logger.log_error(insert_result)
            raise RuntimeError(insert_result.message)


    gitlab_etl()


gitlab_etl()



if __name__ == "__main__":
    dag_instance = gitlab_etl()
    dag_instance.test()