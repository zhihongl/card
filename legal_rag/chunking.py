"""Legal-aware chunking: prefer paragraph boundaries, keep sequence for provenance."""

from __future__ import annotations

import re
import uuid

from legal_rag.metadata import utc_now
from legal_rag.models import ChunkRecord, SourceDocument


def _split_paragraphs(text: str) -> list[str]:
    parts = re.split(r"\n\s*\n+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def chunk_document(
    doc: SourceDocument,
    plain_text: str,
    *,
    max_chars: int = 1800,
    system_user: str,
) -> list[ChunkRecord]:
    """Split document into chunks with stable sequence and provenance."""
    stripped = plain_text.strip()
    paragraphs = _split_paragraphs(plain_text) or ([stripped] if stripped else [])
    chunks: list[ChunkRecord] = []
    buf = ""
    seq = 0

    def flush() -> None:
        nonlocal buf, seq
        if not buf.strip():
            return
        seq += 1
        cid = f"{doc.document_id}-{seq}"
        chunks.append(
            ChunkRecord(
                system_user=system_user,
                update_time=utc_now(),
                chunk_id=cid,
                document_id=doc.document_id,
                source_url=doc.source_url,
                sequence=seq,
                text=buf.strip(),
            )
        )
        buf = ""

    for p in paragraphs:
        if len(buf) + len(p) + 2 <= max_chars:
            buf = f"{buf}\n\n{p}" if buf else p
        else:
            flush()
            if len(p) <= max_chars:
                buf = p
            else:
                for i in range(0, len(p), max_chars):
                    buf = p[i : i + max_chars]
                    flush()
                buf = ""
    flush()
    if not chunks and plain_text.strip():
        chunks.append(
            ChunkRecord(
                system_user=system_user,
                update_time=utc_now(),
                chunk_id=f"{doc.document_id}-1",
                document_id=doc.document_id,
                source_url=doc.source_url,
                sequence=1,
                text=plain_text.strip()[:max_chars],
            )
        )
    return chunks


def new_document_id(source_url: str) -> str:
    return uuid.uuid5(uuid.NAMESPACE_URL, source_url).hex[:16]
