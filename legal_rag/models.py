from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from legal_rag.metadata import Governed


class ManifestEntry(Governed):
    source_url: str
    status: Literal["pending", "success", "failed"]
    checksum_sha256: str | None = None
    http_status: int | None = None
    error_message: str | None = None
    bytes_written: int | None = None
    local_path: str | None = None


class SourceDocument(Governed):
    document_id: str
    source_url: str
    court: str = "Supreme Court of Victoria"
    format: Literal["pdf", "html", "unknown"] = "unknown"
    checksum_sha256: str
    raw_storage_path: str


class ChunkRecord(Governed):
    chunk_id: str
    document_id: str
    source_url: str
    sequence: int
    text: str
    heading_path: str | None = None
    page_start: int | None = None
    page_end: int | None = None


class CitationModel(BaseModel):
    chunk_id: str
    document_id: str
    source_url: str
    label: str
    page_or_span: str | None = None


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k_semantic: int | None = None
    top_k_keyword: int | None = None
    trace_id: str | None = None


class QueryResponse(BaseModel):
    answer: str
    citations: list[CitationModel]
    evidence_sufficient: bool
    retrieval_trace_id: str
    model_versions: dict[str, str]
    degraded: bool = False


class HealthResponse(BaseModel):
    status: str
    postgres: str
    opensearch: str
    timestamp: datetime
    chunks_loaded: int = 0
