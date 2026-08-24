"""Unit tests for CreateLinkRequest's URL validation - the highest-value
suite in the app (docs/test-strategy.md): this is where the one significant
security risk lives, and where M2's own review found a validation approach
that looked right but silently rewrote input (see main.py history)."""
import pytest
from pydantic import ValidationError

from snip.models import CreateLinkRequest

VALID_URLS = [
    "https://example.com",
    "http://example.com/path?query=1",
    "https://example.com:8443/path",
    "https://Example.COM/MixedCase",
]

INVALID_URLS = [
    "javascript:alert(1)",
    "data:text/html,<script>alert(1)</script>",
    "not a url",
    "ftp://example.com",
    "",
]


@pytest.mark.parametrize("url", VALID_URLS)
def test_accepts_well_formed_http_urls(url):
    # Stored exactly as submitted - not normalized/rewritten.
    assert CreateLinkRequest(url=url).url == url


@pytest.mark.parametrize("url", INVALID_URLS)
def test_rejects_unsafe_or_malformed_urls(url):
    with pytest.raises(ValidationError):
        CreateLinkRequest(url=url)
