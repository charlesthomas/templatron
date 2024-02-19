FROM debian:bookworm-slim AS build

RUN apt-get update \
 && apt-get install --no-install-recommends --no-install-suggests --yes git python3-venv \
 && apt-get clean

RUN python3 -m venv /venv \
 && /venv/bin/pip install --upgrade pip poetry setuptools

WORKDIR /app

COPY ./pyproject.toml ./poetry.lock /app
COPY ./README.md /app
COPY ./templatron/ /app/templatron/

RUN /venv/bin/poetry install --without=dev

ENV PYTHONPATH=/app

ENTRYPOINT ["/venv/bin/poetry", "run"]
