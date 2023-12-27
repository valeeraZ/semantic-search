from typing import Generator

import pytest
from starlette.testclient import TestClient

from api.web.application import get_app


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    with TestClient(get_app()) as c:
        yield c
