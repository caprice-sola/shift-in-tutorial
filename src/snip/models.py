"""Request/response models."""

from urllib.parse import urlsplit

from pydantic import BaseModel, field_validator

ALLOWED_SCHEMES = {"http", "https"}


class CreateLinkRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def must_be_safe_http_url(cls, url: str) -> str:
        # Validate only; never normalise, so the stored URL stays exactly what was submitted.
        if any(ch.isspace() or ord(ch) < 32 or ord(ch) == 127 for ch in url):
            raise ValueError("url must not contain whitespace or control characters")
        parts = urlsplit(url)
        if parts.scheme.lower() not in ALLOWED_SCHEMES or not parts.hostname:
            raise ValueError("url must be an absolute http(s) URL with a host")
        if "@" in parts.netloc:
            raise ValueError("url must not contain credentials before the host")
        return url


class LinkResponse(BaseModel):
    code: str
    url: str
    clicks: int

    @classmethod
    def from_record(cls, record: "object") -> "LinkResponse":
        return cls(code=record.code, url=record.url, clicks=record.clicks)
