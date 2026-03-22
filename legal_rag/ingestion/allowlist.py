from __future__ import annotations

from urllib.parse import urlparse

DEFAULT_ALLOWED_HOSTS = frozenset(
    {
        "www.supremecourt.vic.gov.au",
        "supremecourt.vic.gov.au",
    }
)


def is_allowlisted(url: str, hosts: frozenset[str] | None = None) -> bool:
    hosts = hosts or DEFAULT_ALLOWED_HOSTS
    try:
        p = urlparse(url)
    except Exception:
        return False
    if p.scheme not in ("http", "https"):
        return False
    return p.netloc.lower() in hosts
