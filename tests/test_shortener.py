"""Unit tests for snip.shortener."""

from snip import shortener
from snip.store import store


def test_code_collision_does_not_overwrite_existing_link(monkeypatch):
    """generate_code() can produce the same code twice in a row (a
    collision). create_link() must retry until it gets a code that isn't
    already in the store, so an existing link is never silently
    overwritten (SLI 3: resolve correctness — the original link must keep
    resolving to the exact URL it was created for)."""
    store._links.clear()
    # First create_link() draws "AAAAAA". Second create_link()'s first
    # draw collides with it ("AAAAAA" again) and must retry to "BBBBBB".
    codes = iter(["AAAAAA", "AAAAAA", "BBBBBB"])
    monkeypatch.setattr(shortener, "generate_code", lambda: next(codes))

    first = shortener.create_link("https://example.com/first")
    second = shortener.create_link("https://example.com/second")

    assert first.code == "AAAAAA"
    assert second.code == "BBBBBB"
    assert shortener.stats(first.code).url == "https://example.com/first"
    assert shortener.stats(second.code).url == "https://example.com/second"
