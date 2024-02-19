# Semantic Search API

[![codecov](https://codecov.io/gh/valeeraZ/semantic-search/graph/badge.svg?token=DB6E23CCLR)](https://codecov.io/gh/valeeraZ/semantic-search)

Semantic Search is a project aimed at providing efficient search capabilities by leveraging semantic similarity between documents. This project utilizes FastAPI for the backend, PostgreSQL for data storage, and the OpenAI text-embedding-ada-002 model for calculating embedding vectors.

## Features

- FastAPI Backend: Utilizes `FastAPI` for building efficient and fast web APIs.
- PostgreSQL Database: Stores and manages documents and their corresponding embedding vectors using `psycopg2`, `pgvector` with `SQLAlchemy` as the ORM.
- Semantic Search: Search documents using cosine distance for semantic similarity.

## Running the Project

1. Set your openai API key in the `.env` file.
    ```bazaar
    OPENAI_API_KEY=your_api_key
    ```
2. By using Docker: `docker-compose up --build`

3. Without Docker:
    - Use poetry to install dependencies: `poetry install`
    - Enter the virtual environment: `poetry shell`
    - Set up a PostgreSQL database and update the `.env` file with corresponding database credentials.
    ```bazaar
    DB_HOST=localhost
    DB_PORT=5432
    DB_PASS=postgres
    DB_USER=postgres
    DB_BASE=semantic_search
    ```
    - Run the project using `python -m api`
