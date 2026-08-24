"""Shared fixtures. snip.store.store is a module-level singleton, so every
test that goes through shortener/main must start from an empty store."""
import pytest

from snip.store import store


@pytest.fixture(autouse=True)
def clean_store():
    store._links.clear()
    yield
