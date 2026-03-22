# WI-000001 — Technical Specification: Victoria Supreme Court Legal RAG

**Related:** `requirements.md`  
**Status:** Approved (auto-approved)

---

## 1. System overview

The system provides hybrid retrieval over a fixed MVP corpus of ~50 Supreme Court of Victoria judgments and generates short answers with citations using OpenAI. Keyword search uses **OpenSearch (BM25)**; semantic search uses **PostgreSQL + pgvector**. A retrieval orchestrator runs both legs in parallel, fuses results with **RRF**, optionally reranks, then constructs a grounded LLM prompt.

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│  Official   │────▶│ Ingestion +      │────▶│ Raw store + │
│  sources    │     │ manifest         │     │ metadata DB │
└─────────────┘     └──────────────────┘     └──────┬──────┘
                                                    │
                    ┌──────────────────┐            ▼
                    │ Parse + chunk +  │     ┌─────────────┐
                    │ enrich           │◀────│ Documents   │
└──────────────────┴────────┬─────────┘     └─────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
       ┌─────────────┐             ┌─────────────┐
       │ OpenSearch  │             │ pgvector    │
       │ (BM25)      │             │ (embeddings)│
       └──────┬──────┘             └──────┬──────┘
              │                         │
              └────────────┬────────────┘
                           ▼
                    ┌─────────────┐
                    │ RRF fusion  │──▶ optional rerank
                    └──────┬──────┘
                           ▼
                    ┌─────────────┐
                    │ OpenAI      │──▶ answer + citations
                    │ generation  │
                    └─────────────┘
```

---

## 2. Interfaces

### 2.1 Public API (MVP)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/query` | POST | User question → answer, citations, sufficiency flag |
| `/health` | GET | Liveness/readiness |
| `/debug/retrieve` | POST | Retrieval-only diagnostics (auth-gated in prod) |

**Request (query):** `{ "question": string, "top_k_semantic"?: number, "top_k_keyword"?: number, "trace_id"?: string }`  
**Response:** `{ "answer": string, "citations": Citation[], "evidence_sufficient": boolean, "retrieval_trace_id": string, "model_versions": { ... } }`

**Citation object:** `{ "chunk_id": string, "document_id": string, "source_url": string, "label": string, "page_or_span"?: string }`

### 2.2 Operator interfaces

- CLI or job entrypoints: `ingest`, `parse`, `index`, `reindex`, `eval`.
- Configuration via environment variables and a single validated config module (no secrets in repo).

---

## 3. Data model (logical)

All tables/entities below include **`system_user`** and **`update_time`** on every insert/update.

### 3.1 Core entities

- **SourceDocument:** canonical id, source_url, court, judgment_date, case_identifier, format (pdf|html), checksum, raw_storage_uri, ingest_status, parser_version.
- **IngestionManifestRow:** source_url, attempted_at, completed_at, status, error_code, checksum, source_document_id.
- **ParsedDocument:** source_document_id, normalized_text_uri or blob ref, extraction_stats, language.
- **Chunk:** chunk_id, parsed_document_id, sequence, text, heading_path?, page_start?, page_end?, char_offset_start?, char_offset_end?, token_count.
- **EmbeddingRecord:** chunk_id, embedding_model_id, vector, dimensions.
- **OpenSearchDocument:** chunk_id + searchable text + denormalized metadata for filtering.

### 3.2 Audit / run metadata

- **QueryAudit** (optional table or log sink): timestamp, anonymized_user_or_app_id, question_hash, retrieval_trace_id, chunk_ids_retrieved, answer_checksum, llm_model, embedding_model.

---

## 4. Retrieval specification

### 4.1 Semantic leg

- Embed query with same model/version as corpus chunks.
- pgvector similarity search returning `top_k_semantic` with score and chunk metadata.

### 4.2 Keyword leg

- OpenSearch multi_match or equivalent over chunk text + key metadata fields; return `top_k_keyword`.

### 4.3 Fusion

- **RRF** with configurable `k` (default aligned with common practice, e.g. `k=60`) and optional per-leg weights documented in config.
- Deduplicate by `chunk_id` after fusion while preserving best rank contribution.

### 4.4 Reranking (optional)

- If enabled, rerank top `N` fused candidates; `N` and model configurable.

### 4.5 Timeouts

- Per-leg deadline; if one leg fails, respond with keyword-only or semantic-only with explicit `degraded: true` in trace (not necessarily exposed to end users except via debug).

---

## 5. Generation specification

- **Context assembly:** Only fused chunks (post-rerank if enabled) within token budget; include chunk id and citation label in each block.
- **Prompt rules:** Answer only from provided context; if insufficient, state so; every factual claim must reference chunk ids inline or in a structured citation list matching the schema.
- **Validation:** Parse LLM output citations; ensure every cited `chunk_id` ⊆ retrieved set; on failure, retry once with repair instruction or return safe fallback.

---

## 6. Configuration (non-exhaustive)

- `OPENAI_API_KEY`, `OPENAI_CHAT_MODEL`, `OPENAI_EMBEDDING_MODEL`
- `DATABASE_URL` (Postgres + pgvector)
- `OPENSEARCH_URL`, credentials
- `SOURCE_ALLOWLIST_PATH` or inline list versioned in repo for MVP
- `RRF_K`, `TOP_K_SEMANTIC`, `TOP_K_KEYWORD`, feature flags for reranker

---

## 7. Technology constraints

- **Language:** Implementation language chosen in Phase 2 (Python recommended for RAG ecosystem; alternative acceptable if CI and packaging match repo standards).
- **LLM:** OpenAI API.
- **Indexes:** OpenSearch + pgvector as specified; no replacement without ADR.

---

## 8. Quality gates

- Offline **eval set**: held-out questions with expected supporting chunk ids (manual or semi-automatic labeling).
- Minimum thresholds: citation validity rate, groundedness score, and “no-answer when appropriate” cases before widening corpus or model spend.

---

## 9. Traceability

- Each answer exposes `retrieval_trace_id` correlating logs, optional export of chunk list and scores in debug mode.

---

## 10. Spec approval

**Approved:** Yes (auto-approved). Changes after MVP require revision of this document and `requirements.md`.
