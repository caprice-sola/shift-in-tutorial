"""Request/response models."""

from datetime import datetime, timezone
from urllib.parse import urlparse

from pydantic import BaseModel, field_validator

ALLOWED_SCHEMES = {"http", "https"}


class CreateLinkRequest(BaseModel):
    url: str
    expires_at: datetime | None = None

    @field_validator("url")
    @classmethod
    def url_must_be_safe(cls, value: str) -> str:
        # Validate with urlparse rather than pydantic's HttpUrl: HttpUrl silently
        # normalizes (adds a trailing slash, lowercases the host, strips default
        # ports) and caps length at 2083 chars, both of which would break "resolves
        # to the exact URL it was created for" and reject the long SSO/signed-URL
        # links this app exists to shorten. This checks safety without rewriting input.
        parsed = urlparse(value)
        if parsed.scheme not in ALLOWED_SCHEMES or not parsed.netloc:
            raise ValueError("url must be a well-formed http:// or https:// URL")
        return value

    @field_validator("expires_at")
    @classmethod
    def expires_at_must_be_future_utc(cls, value: datetime | None) -> datetime | None:
        # docs/link-expiry-acceptance-criteria.md Rule 2: no offset given -> assume
        # UTC (not the local server's zone); a value already in the past is rejected
        # at creation, same posture as unsafe URLs - reject at the boundary, don't
        # accept and fail later.
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        if value <= datetime.now(timezone.utc):
            raise ValueError("expires_at must be in the future")
        return value


class LinkResponse(BaseModel):
    code: str
    url: str
    clicks: int
    expires_at: datetime | None = None

    @classmethod
    def from_record(cls, record: "object") -> "LinkResponse":
        return cls(
            code=record.code,
            url=record.url,
            clicks=record.clicks,
            expires_at=record.expires_at,
        )
