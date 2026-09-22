"""Unit tests for snip.models.

Ordered per docs/test-strategy.md's SLI -> test level mapping — same scope
notes as tests/unit/test_shortener.py apply here.
"""

from snip.models import CreateLinkRequest, LinkResponse
from snip.store import LinkRecord


# --- SLI 3: Resolve correctness — the URL must survive the request/
# response models unchanged. -----------------------------------------------

def test_create_link_request_preserves_the_url_unchanged():
    url = "https://example.com/a/b?c=d#e"
    assert CreateLinkRequest(url=url).url == url


def test_link_response_from_record_copies_code_and_url_exactly():
    record = LinkRecord(code="AAAAAA", url="https://example.com/target", clicks=3)
    response = LinkResponse.from_record(record)
    assert response.code == "AAAAAA"
    assert response.url == "https://example.com/target"


# --- SLI 5: Stats accuracy — the clicks count must survive the response
# model unchanged. ----------------------------------------------------------

def test_link_response_from_record_copies_clicks_exactly():
    record = LinkRecord(code="AAAAAA", url="https://example.com/target", clicks=3)
    assert LinkResponse.from_record(record).clicks == 3


# --- Deliberately left untested here --------------------------------------
#
# - CreateLinkRequest rejecting an invalid/unsafe url: SLI 4 (create
#   validation). There is no validation logic on CreateLinkRequest yet —
#   url is a bare `str` — so there is nothing to unit-test rejecting. Same
#   deliberate gap noted in tests/unit/test_shortener.py.
