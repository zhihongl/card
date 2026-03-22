from __future__ import annotations

from legal_rag.config import Settings
from legal_rag.models import ChunkRecord, QueryResponse
from legal_rag.rag.citations import chunks_to_citation_models, validate_citations


def _context_block(chunks: list[ChunkRecord]) -> str:
    parts: list[str] = []
    for c in chunks:
        parts.append(f"### Evidence chunk_id={c.chunk_id}\n{c.text[:6000]}")
    return "\n\n".join(parts)


def generate_answer(
    question: str,
    chunks: list[ChunkRecord],
    settings: Settings,
    *,
    trace_id: str,
) -> QueryResponse:
    citations = chunks_to_citation_models(chunks)
    allowed = {c.chunk_id for c in chunks}
    model_versions = {
        "chat": settings.openai_chat_model if settings.openai_api_key else "offline-template",
        "embedding": settings.openai_embedding_model if settings.openai_api_key else "mock-hash",
    }

    if not chunks:
        return QueryResponse(
            answer="Insufficient evidence in the corpus for this question.",
            citations=[],
            evidence_sufficient=False,
            retrieval_trace_id=trace_id,
            model_versions=model_versions,
        )

    if not settings.openai_api_key:
        preview = "\n".join(f"- [{c.chunk_id}]: {c.text[:200]}…" for c in chunks[:5])
        msg = "OPENAI_API_KEY is not set; showing retrieved excerpts only (no LLM synthesis).\n\n"
        answer = msg + preview
        return QueryResponse(
            answer=answer,
            citations=citations,
            evidence_sufficient=True,
            retrieval_trace_id=trace_id,
            model_versions=model_versions,
            degraded=True,
        )

    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    system = (
        "You are a legal research assistant. Answer ONLY using the evidence blocks. "
        "Every factual claim must end with a bracketed chunk_id reference like [docid-1]. "
        "If evidence is insufficient, say so explicitly."
    )
    user = f"Question:\n{question}\n\nEvidence:\n{_context_block(chunks)}"
    resp = client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.2,
    )
    answer = resp.choices[0].message.content or ""
    ok, bad = validate_citations(answer, allowed)
    if not ok:
        answer = (
            "The model cited chunk ids not present in the retrieved set "
            f"({bad}). Insufficient validated answer."
        )
        return QueryResponse(
            answer=answer,
            citations=citations,
            evidence_sufficient=False,
            retrieval_trace_id=trace_id,
            model_versions=model_versions,
            degraded=True,
        )

    return QueryResponse(
        answer=answer,
        citations=citations,
        evidence_sufficient=True,
        retrieval_trace_id=trace_id,
        model_versions=model_versions,
    )


def debug_retrieval_json(question: str, chunks: list[ChunkRecord], trace_id: str) -> dict:
    return {
        "trace_id": trace_id,
        "question": question,
        "chunk_ids": [c.chunk_id for c in chunks],
        "sources": list({c.source_url for c in chunks}),
    }
