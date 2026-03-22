from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from legal_rag.config import Settings, get_settings
from legal_rag.ingestion.pipeline import load_chunks_from_disk
from legal_rag.models import ChunkRecord, HealthResponse, QueryRequest, QueryResponse
from legal_rag.rag.answer import debug_retrieval_json, generate_answer
from legal_rag.retrieval.hybrid import hybrid_retrieve

logger = logging.getLogger(__name__)

_STORE: list[ChunkRecord] = []


def _chunks_path(settings: Settings) -> Path:
    env = os.environ.get("LEGAL_RAG_CHUNKS_PATH")
    if env:
        return Path(env)
    return Path(settings.data_dir) / "processed" / "chunks.jsonl"


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    path = _chunks_path(settings)
    global _STORE
    _STORE = load_chunks_from_disk(path)
    logger.info("Loaded %s chunks from %s", len(_STORE), path)
    yield


app = FastAPI(title="Legal RAG (WI-000001)", lifespan=lifespan)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    pg = "not_configured"
    os_status = "not_configured"
    if settings.database_url:
        try:
            import psycopg

            with psycopg.connect(settings.database_url, connect_timeout=3) as conn:
                conn.execute("SELECT 1")
            pg = "ok"
        except Exception as exc:  # noqa: BLE001
            pg = f"error: {exc.__class__.__name__}"
    if settings.opensearch_url:
        try:
            from legal_rag.indexing.sync import _os_client

            c = _os_client(settings)
            h = c.cluster.health()
            os_status = str(h.get("status", "unknown"))
        except Exception as exc:  # noqa: BLE001
            os_status = f"error: {exc.__class__.__name__}"
    overall = "ok" if _STORE else "degraded"
    return HealthResponse(
        status=overall,
        postgres=pg,
        opensearch=os_status,
        timestamp=datetime.now(UTC),
        chunks_loaded=len(_STORE),
    )


@app.post("/query", response_model=QueryResponse)
def query(body: QueryRequest) -> QueryResponse:
    settings = get_settings()
    if body.top_k_semantic is not None:
        settings.top_k_semantic = body.top_k_semantic
    if body.top_k_keyword is not None:
        settings.top_k_keyword = body.top_k_keyword
    chunks, trace_id = hybrid_retrieve(body.question, _STORE, settings)
    top = chunks[:12]
    return generate_answer(body.question, top, settings, trace_id=trace_id)


@app.post("/debug/retrieve")
def debug_retrieve(body: QueryRequest) -> JSONResponse:
    settings = get_settings()
    chunks, trace_id = hybrid_retrieve(body.question, _STORE, settings)
    return JSONResponse(debug_retrieval_json(body.question, chunks[:20], trace_id))


def create_app() -> FastAPI:
    return app
