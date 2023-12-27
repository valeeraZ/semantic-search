FROM python:3.11.4-slim-bullseye as prod


RUN apt-get update && apt-get install -y \
  gcc \
  && rm -rf /var/lib/apt/lists/*

# Installing psycopg2 dependencies
RUN apt-get update && apt-get install -y \
  libpq-dev \
  && rm -rf /var/lib/apt/lists/*

RUN pip install poetry==1.4.2

# Configuring poetry
RUN poetry config virtualenvs.create false

# Copying requirements of a project
COPY pyproject.toml poetry.lock /app/src/
WORKDIR /app/src

# Copying actuall application
COPY ./api /app/src/
RUN poetry install --only main

CMD ["/usr/local/bin/python", "-m", "api"]

FROM prod as dev

RUN poetry install
