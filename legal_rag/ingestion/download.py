from __future__ import annotations

import hashlib
import time
from pathlib import Path

import httpx

from legal_rag.ingestion.allowlist import is_allowlisted


class DownloadError(Exception):
    pass


def download_bytes(url: str, *, max_retries: int = 5, timeout: float = 120.0) -> tuple[bytes, int]:
    if not is_allowlisted(url):
        raise DownloadError(f"URL not allowlisted: {url}")
    last_exc: Exception | None = None
    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=timeout, follow_redirects=True) as client:
                r = client.get(url, headers={"User-Agent": "LegalRAG-WI000001/0.1 (research; +https://example.invalid)"})
                r.raise_for_status()
                return r.content, r.status_code
        except Exception as exc:  # noqa: BLE001 — retry broad failures
            last_exc = exc
            time.sleep(min(2**attempt, 30))
    raise DownloadError(f"Failed after {max_retries} attempts: {url}") from last_exc


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)
