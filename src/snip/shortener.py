"""Core shortening logic."""

import random
import string
from datetime import datetime, timezone

from .store import LinkNotFoundError, LinkRecord, store

__all__ = [
    "LinkExpiredError",
    "LinkNotFoundError",
    "create_link",
    "generate_code",
    "list_links",
    "resolve",
    "stats",
]

ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 6


class LinkExpiredError(Exception):
    """Raised when a link exists but its expiry has passed. Distinct from
    LinkNotFoundError: the link was valid and is deliberately gone, which the
    HTTP boundary translates to 410 (not 404) - see main.py."""


def generate_code() -> str:
    return "".join(random.choice(ALPHABET) for _ in range(CODE_LENGTH))


def create_link(url: str, expires_at: datetime | None = None) -> LinkRecord:
    # check-then-act, not atomic: fine for this in-memory, single-process workshop
    # store under test/demo traffic, but not a concurrency guarantee - two
    # requests could still race between exists() and put() under real load.
    code = generate_code()
    while store.exists(code):
        code = generate_code()
    record = LinkRecord(code=code, url=url, expires_at=expires_at)
    store.put(record)
    return record


def resolve(code: str) -> LinkRecord:
    record = store.get(code)
    if record.expires_at is not None and record.expires_at <= datetime.now(timezone.utc):
        # Not a follow (docs/link-expiry-acceptance-criteria.md Rule 4) - raise
        # before incrementing clicks, not after.
        raise LinkExpiredError(code)
    record.clicks += 1
    return record


def stats(code: str) -> LinkRecord:
    return store.get(code)


def list_links() -> list:
    return store.all()
