from __future__ import annotations

import re
from collections.abc import Iterable

from legal_rag.models import ChunkRecord, CitationModel


def chunks_to_citation_models(chunks: Iterable[ChunkRecord]) -> list[CitationModel]:
    out: list[CitationModel] = []
    for c in chunks:
        out.append(
            CitationModel(
                chunk_id=c.chunk_id,
                document_id=c.document_id,
                source_url=c.source_url,
                label=f"[{c.chunk_id}]",
                page_or_span=f"seq {c.sequence}",
            )
        )
    return out


def extract_cited_chunk_ids(answer_text: str) -> set[str]:
    """Parse inline chunk references like [abc-1] or chunk_id tokens from model output."""
    found = set(re.findall(r"\[([a-zA-Z0-9_-]+-[0-9]+)\]", answer_text))
    return found


def validate_citations(answer_text: str, allowed_ids: set[str]) -> tuple[bool, set[str]]:
    cited = extract_cited_chunk_ids(answer_text)
    if not cited:
        return True, set()
    bad = cited - allowed_ids
    return len(bad) == 0, bad
