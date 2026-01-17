"""Test configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.in_memory_store import data_store


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_data_store():
    """Reset data store before each test."""
    data_store.reset()
    yield
    data_store.reset()
