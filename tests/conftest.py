import os

# Set env vars before any app import so Pydantic Settings resolves them
os.environ.setdefault("META_VERIFY_TOKEN", "test_token")
os.environ.setdefault("META_APP_SECRET", "test_secret")
os.environ.setdefault("PAGE_ACCESS_TOKEN", "test_page_token")

import pytest
from fastapi.testclient import TestClient

from app import create_app


@pytest.fixture(scope="session")
def app():
    return create_app()


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c
