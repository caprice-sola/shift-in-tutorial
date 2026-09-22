"""Unit tests for snip.shortener.

Ordered per docs/test-strategy.md's SLI -> test level mapping. SLI 1 and 2
have no Unit row in that table (SLI 1 is a separate performance lane; SLI 2
is proven at Integration + System only) so there's nothing of theirs here
— see the note at the bottom of this file.
"""

import pytest

from snip import shortener
from snip.store import store


@pytest.fixture(autouse=True)
def clear_store():
    """store is a module-level singleton shared across tests; reset it so
    tests don't see each other's records."""
    store._links.clear()
    yield
    store._links.clear()


# --- SLI 3: Resolve correctness — a follow must land on the exact
# stored URL. -------------------------------------------------------------

def test_resolve_returns_the_url_the_link_was_created_with():
    record = shortener.create_link("https://example.com/target")
    resolved = shortener.resolve(record.code)
    assert resolved.url == "https://example.com/target"


def test_stats_returns_the_url_the_link_was_created_with():
    record = shortener.create_link("https://example.com/target")
    assert shortener.stats(record.code).url == "https://example.com/target"


def test_code_collision_does_not_overwrite_existing_link(monkeypatch):
    """generate_code() can produce the same code twice in a row (a
    collision). create_link() must retry until it gets a code that isn't
    already in the store, so an existing link is never silently
    overwritten."""
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


# --- SLI 4: Create validation — no Unit row is exercisable yet; see the
# "deliberately left untested" note below. --------------------------------


# --- SLI 5: Stats accuracy — recorded clicks must equal actual follows. --

def test_resolve_increments_clicks_by_one_per_call():
    record = shortener.create_link("https://example.com/target")
    shortener.resolve(record.code)
    shortener.resolve(record.code)
    assert shortener.stats(record.code).clicks == 2


def test_stats_does_not_increment_clicks():
    """Checking stats is a read, not a follow — it must not itself count
    as a click."""
    record = shortener.create_link("https://example.com/target")
    shortener.stats(record.code)
    shortener.stats(record.code)
    assert shortener.stats(record.code).clicks == 0


# --- Deliberately left untested here --------------------------------------
#
# - resolve()/stats() on an unknown code (KeyError -> 404 at the HTTP
#   layer): that's SLI 2, and docs/test-strategy.md proves SLI 2 at
#   Integration ("404 contract") and System level, not Unit. Belongs in
#   tests/integration/, not here.
# - Redirect latency (SLI 1): not a correctness assertion at all per
#   test-strategy.md ("doesn't fit the pyramid") — its own performance
#   check, not a unit test.
# - Create validation (SLI 4): CreateLinkRequest.url is a bare `str` with
#   no validation rules yet, so there is nothing to unit-test rejecting —
#   this is the deliberate gap docs/slis.md flags for M2's review, closed
#   in a later milestone.
# - generate_code()'s charset/length: no SLI measures code format itself,
#   only the values it produces once stored.
# - list_links(): no SLI in docs/slis.md covers the list endpoint.
