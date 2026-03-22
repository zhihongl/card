"""Embeddings: OpenAI when configured, else deterministic mock vectors (CI / offline)."""

from __future__ import annotations

import hashlib
import struct
from collections.abc import Sequence

from legal_rag.config import Settings


def _mock_vector(text: str, dimensions: int) -> list[float]:
    h = hashlib.sha256(text.encode()).digest()
    out: list[float] = []
    for i in range(dimensions):
        chunk = h[i % len(h) : (i % len(h)) + 4] or h[:4]
        if len(chunk) < 4:
            chunk = (chunk + h)[:4]
        (val,) = struct.unpack("!I", chunk.ljust(4, b"\0")[:4])
        out.append((val % 10_000) / 10_000.0)
    return out


def embed_query(text: str, settings: Settings) -> list[float]:
    if settings.openai_api_key:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        res = client.embeddings.create(model=settings.openai_embedding_model, input=text)
        return list(res.data[0].embedding)
    return _mock_vector(text, settings.embedding_dimensions)


def embed_documents(texts: Sequence[str], settings: Settings) -> list[list[float]]:
    if settings.openai_api_key:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        res = client.embeddings.create(model=settings.openai_embedding_model, input=list(texts))
        return [list(d.embedding) for d in res.data]
    return [_mock_vector(t, settings.embedding_dimensions) for t in texts]
