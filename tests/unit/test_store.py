"""Unit tests for the in-memory Store. Uses fresh Store() instances rather
than the app-wide singleton, since Store itself is trivially instantiable."""
import pytest

from snip.store import LinkNotFoundError, LinkRecord, Store


def test_put_and_get_round_trip():
    store = Store()
    record = LinkRecord(code="abc123", url="https://example.com")
    store.put(record)
    assert store.get("abc123") is record


def test_get_missing_code_raises_link_not_found():
    store = Store()
    with pytest.raises(LinkNotFoundError):
        store.get("nope")


def test_exists_true_for_known_code():
    store = Store()
    store.put(LinkRecord(code="abc123", url="https://example.com"))
    assert store.exists("abc123") is True


def test_exists_false_for_unknown_code():
    assert Store().exists("nope") is False


def test_all_returns_every_stored_record():
    store = Store()
    store.put(LinkRecord(code="a", url="https://example.com/a"))
    store.put(LinkRecord(code="b", url="https://example.com/b"))
    assert {r.code for r in store.all()} == {"a", "b"}


def test_put_overwrites_existing_code():
    # Store itself has no opinion on collisions - preventing them is
    # shortener.create_link's job. See
    # test_shortener.py::test_create_link_retries_on_code_collision.
    store = Store()
    store.put(LinkRecord(code="abc123", url="https://example.com/first"))
    store.put(LinkRecord(code="abc123", url="https://example.com/second"))
    assert store.get("abc123").url == "https://example.com/second"
