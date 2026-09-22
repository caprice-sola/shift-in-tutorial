"""Unit tests for snip.store.

Ordered per docs/test-strategy.md's SLI -> test level mapping — same scope
notes as tests/unit/test_shortener.py apply here.
"""

from snip.store import LinkRecord, Store


# --- SLI 3: Resolve correctness — a follow must land on the exact
# stored URL. -------------------------------------------------------------

def test_get_returns_the_record_put_under_its_code():
    store = Store()
    store.put(LinkRecord(code="AAAAAA", url="https://example.com/target"))
    assert store.get("AAAAAA").url == "https://example.com/target"


def test_exists_is_true_for_a_stored_code_and_false_otherwise():
    store = Store()
    store.put(LinkRecord(code="AAAAAA", url="https://example.com/target"))
    assert store.exists("AAAAAA") is True
    assert store.exists("BBBBBB") is False


# --- Deliberately left untested here --------------------------------------
#
# - get() on a missing code (KeyError -> 404 at the HTTP layer): SLI 2,
#   proven at Integration/System per docs/test-strategy.md, not Unit.
# - put() overwriting an existing code: this is the mechanism behind the
#   collision bug, but it's already exercised end-to-end by
#   tests/unit/test_shortener.py::test_code_collision_does_not_overwrite_existing_link
#   — skipping a duplicate store-only test of the same behaviour.
# - all(): no SLI in docs/slis.md covers the list endpoint.
