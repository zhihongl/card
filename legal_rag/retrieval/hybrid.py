from __future__ import annotations

import math
import re
import uuid

from legal_rag.config import Settings
from legal_rag.embedding import embed_query
from legal_rag.models import ChunkRecord
from legal_rag.retrieval.rrf import reciprocal_rank_fusion

_CHUNK_VEC_CACHE: dict[str, list[float]] = {}


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _keyword_rank(question: str, chunks: list[ChunkRecord]) -> list[ChunkRecord]:
    terms = [t.lower() for t in re.findall(r"[a-zA-Z]{3,}", question.lower())]
    scored: list[tuple[float, ChunkRecord]] = []
    for c in chunks:
        text_l = c.text.lower()
        score = sum(text_l.count(t) for t in terms)
        scored.append((float(score), c))
    scored.sort(key=lambda x: -x[0])
    return [c for s, c in scored if s > 0] or list(chunks)[:8]


def hybrid_retrieve(
    question: str,
    chunks: list[ChunkRecord],
    settings: Settings,
) -> tuple[list[ChunkRecord], str]:
    """Parallel semantic (cosine on embeddings) + keyword; fuse with RRF."""
    trace_id = str(uuid.uuid4())
    if not chunks:
        return [], trace_id

    q_vec = embed_query(question, settings)
    chunk_vecs: list[list[float]] = []
    for c in chunks:
        if c.chunk_id not in _CHUNK_VEC_CACHE:
            _CHUNK_VEC_CACHE[c.chunk_id] = embed_query(c.text[:2000], settings)
        chunk_vecs.append(_CHUNK_VEC_CACHE[c.chunk_id])

    sem_order: list[str] = sorted(
        range(len(chunks)),
        key=lambda i: -_cosine(q_vec, chunk_vecs[i]),
    )
    sem_ids = [chunks[i].chunk_id for i in sem_order[: settings.top_k_semantic]]

    kw_ordered = _keyword_rank(question, chunks)
    kw_ids = [c.chunk_id for c in kw_ordered[: settings.top_k_keyword]]

    fused_ids = reciprocal_rank_fusion([sem_ids, kw_ids], k=settings.rrf_k)
    by_id = {c.chunk_id: c for c in chunks}
    ordered = [by_id[i] for i in fused_ids if i in by_id]
    return ordered, trace_id
