FROM apache/airflow:3.2.2

COPY requirements.txt .

USER airflow

RUN pip install --no-cache-dir -r requirements.txt