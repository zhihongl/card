from __future__ import annotations

from pathlib import Path

import httpx

from legal_rag.chunking import chunk_document, new_document_id
from legal_rag.config import Settings
from legal_rag.ingestion.discover import extract_judgment_urls
from legal_rag.ingestion.download import DownloadError, download_bytes, sha256_hex, write_atomic
from legal_rag.metadata import utc_now
from legal_rag.models import ChunkRecord, ManifestEntry, SourceDocument
from legal_rag.parsing.extract import extract_from_html, extract_from_pdf


def _detect_format(url: str, content_type: str | None, body: bytes) -> str:
    u = url.lower()
    if u.endswith(".pdf") or "pdf" in (content_type or "").lower():
        return "pdf"
    if b"%PDF" in body[:5]:
        return "pdf"
    return "html"


def fetch_listing_page(list_url: str, page: int) -> str:
    sep = "&" if "?" in list_url else "?"
    url = f"{list_url}{sep}page={page}"
    with httpx.Client(timeout=60.0, follow_redirects=True) as client:
        r = client.get(
            url,
            headers={"User-Agent": "LegalRAG-WI000001/0.1 (research)"},
        )
        r.raise_for_status()
    return r.text


def discover_up_to(settings: Settings) -> list[str]:
    seen: set[str] = set()
    for page in range(settings.max_listing_pages):
        html = fetch_listing_page(settings.judgments_list_url, page)
        found = extract_judgment_urls(html, settings.judgments_list_url)
        for u in found:
            seen.add(u)
        if len(seen) >= settings.max_ingest_documents:
            break
    return sorted(seen)[: settings.max_ingest_documents]


def ingest_all(
    settings: Settings,
    *,
    system_user: str,
    raw_dir: Path | None = None,
    processed_dir: Path | None = None,
) -> tuple[list[ManifestEntry], list[ChunkRecord]]:
    raw_dir = raw_dir or Path(settings.data_dir) / "raw"
    processed_dir = processed_dir or Path(settings.data_dir) / "processed"
    manifest_path = processed_dir / "manifest.jsonl"
    chunks_path = processed_dir / "chunks.jsonl"
    processed_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text("", encoding="utf-8")
    chunks_path.write_text("", encoding="utf-8")

    urls = discover_up_to(settings)
    manifest: list[ManifestEntry] = []
    all_chunks: list[ChunkRecord] = []

    for url in urls:
        entry = ManifestEntry(
            system_user=system_user,
            update_time=utc_now(),
            source_url=url,
            status="pending",
        )
        try:
            body, status = download_bytes(url)
            digest = sha256_hex(body)
            fmt = _detect_format(url, None, body)
            ext = ".pdf" if fmt == "pdf" else ".html"
            doc_id = new_document_id(url)
            out = raw_dir / f"{digest[:12]}{ext}"
            write_atomic(out, body)
            entry.checksum_sha256 = digest
            entry.http_status = status
            entry.bytes_written = len(body)
            entry.local_path = str(out)
            entry.status = "success"

            if fmt == "pdf":
                text = extract_from_pdf(body)
            else:
                text = extract_from_html(body)

            doc = SourceDocument(
                system_user=system_user,
                update_time=utc_now(),
                document_id=doc_id,
                source_url=url,
                format="pdf" if fmt == "pdf" else "html",
                checksum_sha256=digest,
                raw_storage_path=str(out),
            )
            chunks = chunk_document(doc, text, system_user=system_user)
            all_chunks.extend(chunks)
        except (DownloadError, OSError, ValueError) as exc:
            entry.status = "failed"
            entry.error_message = str(exc)[:2000]
        manifest.append(entry)

    with manifest_path.open("a", encoding="utf-8") as mf:
        for m in manifest:
            mf.write(m.model_dump_json() + "\n")
    with chunks_path.open("a", encoding="utf-8") as cf:
        for c in all_chunks:
            cf.write(c.model_dump_json() + "\n")

    return manifest, all_chunks


def load_chunks_from_disk(path: Path) -> list[ChunkRecord]:
    if not path.exists():
        return []
    out: list[ChunkRecord] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        out.append(ChunkRecord.model_validate_json(line))
    return out
