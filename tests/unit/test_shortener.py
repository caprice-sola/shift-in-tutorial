"""Unit tests for shortener.py - the highest-risk logic in the app, and where we
check our oracles by breaking a line on purpose (see docs/test-strategy.md)."""
import pytest

from snip import shortener
from snip.store import LinkNotFoundError


def test_generate_code_length_and_alphabet():
    code = shortener.generate_code()
    assert len(code) == shortener.CODE_LENGTH
    assert set(code) <= set(shortener.ALPHABET)


def test_create_link_stores_exact_url():
    record = shortener.create_link("https://example.com/a/b?c=1")
    assert record.url == "https://example.com/a/b?c=1"
    assert record.clicks == 0


def test_create_link_assigns_a_resolvable_code():
    record = shortener.create_link("https://example.com")
    assert shortener.resolve(record.code).url == "https://example.com"


def test_resolve_increments_click_count():
    record = shortener.create_link("https://example.com")
    assert record.clicks == 0
    shortener.resolve(record.code)
    shortener.resolve(record.code)
    assert shortener.stats(record.code).clicks == 2


def test_resolve_unknown_code_raises_link_not_found():
    with pytest.raises(LinkNotFoundError):
        shortener.resolve("doesnotexist")


def test_stats_unknown_code_raises_link_not_found():
    with pytest.raises(LinkNotFoundError):
        shortener.stats("doesnotexist")


def test_list_links_returns_all_created_links():
    shortener.create_link("https://example.com/1")
    shortener.create_link("https://example.com/2")
    assert {r.url for r in shortener.list_links()} == {
        "https://example.com/1",
        "https://example.com/2",
    }


def test_create_link_retries_on_code_collision(monkeypatch):
    # generate_code returns the same value twice, then a distinct one. A
    # correct create_link must not let the second call silently overwrite
    # the first link - this collision gap was deliberately left unfixed
    # during M2's review for a closer look here.
    codes = iter(["dupe12", "dupe12", "uniq99"])
    monkeypatch.setattr(shortener, "generate_code", lambda: next(codes))

    first = shortener.create_link("https://example.com/first")
    second = shortener.create_link("https://example.com/second")

    assert first.code != second.code
    assert second.code == "uniq99"  # retried via generate_code(), not left blank
    assert shortener.resolve(first.code).url == "https://example.com/first"
    assert shortener.resolve(second.code).url == "https://example.com/second"
