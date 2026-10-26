import pytest
from pydantic import ValidationError

from snip.models import CreateLinkRequest, LinkResponse
from snip.store import LinkRecord


# SLI 3 / SLI 5: the response is what the user sees, so it must carry the stored values exactly.


def test_link_response_carries_code_url_and_clicks_exactly():
    record = LinkRecord(code="abc123", url="https://example.com/a?b=c#d", clicks=4)

    response = LinkResponse.from_record(record)

    assert response.model_dump() == {
        "code": "abc123",
        "url": "https://example.com/a?b=c#d",
        "clicks": 4,
    }


def test_link_response_reflects_the_current_click_count():
    record = LinkRecord(code="abc123", url="https://example.com")
    record.clicks += 1

    assert LinkResponse.from_record(record).clicks == 1


# SLI 4 (type level only): the request model refuses a missing or non-string url.


def test_create_request_requires_a_url():
    with pytest.raises(ValidationError):
        CreateLinkRequest()


def test_create_request_rejects_a_non_string_url():
    with pytest.raises(ValidationError):
        CreateLinkRequest(url=123)


def test_create_request_keeps_the_url_unchanged():
    url = "https://example.com/a?b=c#d"

    assert CreateLinkRequest(url=url).url == url
