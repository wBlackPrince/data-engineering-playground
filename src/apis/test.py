import asyncio
import json
import os
import logging

from clickhouse_driver import Client
from httpx import Response

from apis.app_logger import AppLogger
from apis.gitlab_client import GitlabClient
from apis.result import Result, is_failure
from apis.async_http_client import AsyncHttpClient
from models.gitlab_commit import GitlabCommit

async def run_etl():

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
        logging.exception("Ошибка при десериализации json")
        raise

    logging.info("Начало трансформации данных...")
    
    commits: list[GitlabCommit] = []
    
    for commit_data in commit_data_dict:
        commits.append(GitlabCommit.from_dict(commit_data))
    
    batch: list[tuple] = [commit.to_tuple() for commit in commits]


    logging.info("Начало загрузки данных в ClickHouse...")

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
        logging.exception("Ошибка при загрузке в ClickHouse")
        raise


if __name__ == "__main__":
    asyncio.run(run_etl())