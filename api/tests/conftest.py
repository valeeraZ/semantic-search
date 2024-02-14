from typing import Generator

import pytest
from fastapi import FastAPI
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from api.web.api import api_router


def get_test_app() -> FastAPI:
    app = FastAPI()

    SQLALCHEMY_DATABASE_URL = "sqlite://"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    app.state.db_engine = engine
    app.state.db_session_factory = TestingSessionLocal
    # noqa: F821
    app.include_router(router=api_router, prefix="/api")

    return app


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    with TestClient(get_test_app()) as c:
        yield c
