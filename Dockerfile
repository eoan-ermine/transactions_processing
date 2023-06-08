FROM python:3.10 as transactions_processing
WORKDIR /transactions_processing/

RUN pip install poetry

COPY . .
RUN poetry install --only main

CMD poetry run python3 -m transactions_processing