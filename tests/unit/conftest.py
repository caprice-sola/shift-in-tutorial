import pytest

from snip import shortener
from snip.store import Store


@pytest.fixture(autouse=True)
def fresh_store(monkeypatch):
    """Every test starts from an empty store (strategy: no shared test data)."""
    monkeypatch.setattr(shortener, "store", Store())
