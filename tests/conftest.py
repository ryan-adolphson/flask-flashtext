import pytest

from app import create_app
from app.config import TestingConfig


@pytest.fixture
def app():
    application = create_app(TestingConfig)
    yield application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def valid_headers():
    return {"X-API-Key": "test-key-1", "Content-Type": "application/json"}


@pytest.fixture
def invalid_headers():
    return {"X-API-Key": "wrong-key", "Content-Type": "application/json"}
