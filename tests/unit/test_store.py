import pytest

from snip.store import LinkRecord, Store


# SLI 3 / SLI 5: the store is what holds the exact URL and the click count.


def test_get_returns_the_stored_record_with_exact_url():
    store = Store()
    store.put(LinkRecord(code="abc123", url="https://example.com/a?b=c#d"))

    record = store.get("abc123")

    assert (record.code, record.url, record.clicks) == (
        "abc123",
        "https://example.com/a?b=c#d",
        0,
    )


def test_get_returns_the_live_record_so_a_click_increment_persists():
    store = Store()
    store.put(LinkRecord(code="abc123", url="https://example.com"))

    store.get("abc123").clicks += 1

    assert store.get("abc123").clicks == 1


# SLI 2: unknown codes must be distinguishable so the API can answer 404.


def test_get_unknown_code_raises_keyerror():
    with pytest.raises(KeyError):
        Store().get("nope00")


def test_exists_is_true_only_for_stored_codes():
    store = Store()
    store.put(LinkRecord(code="abc123", url="https://example.com"))

    assert store.exists("abc123") is True
    assert store.exists("ABC123") is False
    assert store.exists("nope00") is False


def test_get_does_not_create_missing_records():
    store = Store()

    with pytest.raises(KeyError):
        store.get("nope00")

    assert store.all() == []


# list endpoint


def test_all_returns_every_record_and_is_a_copy():
    store = Store()
    a = LinkRecord(code="aaaaaa", url="https://a.example")
    b = LinkRecord(code="bbbbbb", url="https://b.example")
    store.put(a)
    store.put(b)

    listed = store.all()
    listed.clear()

    assert [r.code for r in store.all()] == ["aaaaaa", "bbbbbb"]
