import pytest
from fastapi.testclient import TestClient

from snip import shortener
from snip.main import app
from snip.store import Store


@pytest.fixture(autouse=True)
def fresh_store(monkeypatch):
    """Every test starts from an empty store (strategy: no shared test data)."""
    monkeypatch.setattr(shortener, "store", Store())


@pytest.fixture
def client():
    return TestClient(app)
