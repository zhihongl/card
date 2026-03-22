from __future__ import annotations

from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from legal_rag.ingestion.allowlist import is_allowlisted


def extract_judgment_urls(html: str, page_url: str) -> list[str]:
    """Parse listing or detail HTML; return unique judgment-related URLs on allowlisted hosts."""
    soup = BeautifulSoup(html, "lxml")
    found: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith("#") or href.startswith("javascript:"):
            continue
        full = urljoin(page_url, href)
        full = full.split("#")[0]
        if not is_allowlisted(full):
            continue
        path = urlparse(full).path.lower()
        if path.endswith(".pdf") and "/sites/default/files/" in path:
            if any(k in path for k in ("judgment", "summary")):
                found.add(full)
            continue
        if "/areas/case-summaries/judgments/" in path:
            base_j = "/areas/case-summaries/judgments"
            if path.rstrip("/") == base_j or path.rstrip("/") == base_j + "/":
                continue
            found.add(full)
    return sorted(found)
