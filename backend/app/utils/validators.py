from urllib.parse import urlparse

from fastapi import HTTPException, status

TEXT_MIN_LENGTH = 20
TEXT_MAX_LENGTH = 10000
URL_MAX_LENGTH = 2048
ALLOWED_PROTOCOLS = ("http", "https")


def validate_text(content: str) -> str:
    content = content.strip()
    if not content:
        raise ValueError("Content is required")
    if len(content) < TEXT_MIN_LENGTH:
        raise ValueError(f"Content must be at least {TEXT_MIN_LENGTH} characters long")
    if len(content) > TEXT_MAX_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Content must not exceed {TEXT_MAX_LENGTH} characters",
        )
    return content


def validate_url(url: str) -> str:
    url = url.strip()
    if not url:
        raise ValueError("URL is required")
    if len(url) > URL_MAX_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"URL must not exceed {URL_MAX_LENGTH} characters",
        )
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_PROTOCOLS or not parsed.netloc:
        raise ValueError("URL must be a valid http(s) URL")
    return url
