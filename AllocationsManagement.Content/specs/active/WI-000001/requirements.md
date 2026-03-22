# WI-000001 — Victoria Supreme Court Legal RAG Platform

**Status:** Approved (auto-approved for execution)  
**Work item:** WI-000001  
**Jurisdiction (MVP):** Supreme Court of Victoria — published judgments only (official sources)  
**Architecture:** Option A — OpenSearch (keyword/BM25) + PostgreSQL with pgvector (semantic)  
**LLM provider:** OpenAI (cost-optimized model/embedding profile)  
**Initial corpus:** ~50 cases  

---

## 1. Purpose

Define production-ready requirements for a Legal Retrieval-Augmented Generation (RAG) system that ingests official Victorian Supreme Court judgments, indexes them for hybrid retrieval, and returns answers grounded in retrieved evidence with explicit citations.

---

## 2. Scope

### 2.1 In scope (MVP)

- Acquisition of ~50 published judgments (PDF and/or HTML) from **official** Supreme Court of Victoria sources only.
- Persistent storage of raw artifacts, normalized metadata, and processing lineage.
- Document parsing, cleaning, normalization, and legal-aware chunking (headings, sections, citation-aware boundaries where feasible).
- Dual indexing: dense embeddings (pgvector) and lexical/BM25 (OpenSearch).
- Hybrid retrieval with parallel semantic and keyword paths, fusion (RRF), optional reranking.
- Answer generation via OpenAI with strict citation rules, insufficient-evidence handling, and validation hooks.
- HTTP API: query, retrieval debug, health.
- Operational baseline: structured logging, retries, idempotent ingestion/index updates, audit trail, security controls suitable for production hardening.

### 2.2 Out of scope (MVP)

- Non-official or scraped third-party legal databases.
- Procedural notices, listings, or non-judgment court publications.
- Multi-jurisdiction corpora beyond Victoria Supreme Court for MVP.
- Guaranteed legal advice or outcome prediction; the system is an **evidence-grounded research assistant**, not a substitute for professional legal counsel.
- Real-time sync with court feeds (batch or scheduled ingestion is acceptable for MVP).

---

## 3. Metadata policy (mandatory)

Every **created or updated** persistent record (raw artifact registry, document metadata, chunk records, index entries’ backing rows, ingestion manifest rows, audit events where stored as records) MUST include:

| Field          | Description |
|----------------|-------------|
| `system_user`  | Identifier of the system or service principal that performed the create/update (e.g. service account, pipeline job id, or authenticated operator id). |
| `update_time`  | UTC timestamp of the last write, ISO-8601 with timezone (recommended: `Z`). |

**Acceptance:** Automated tests or validation jobs fail if any new/updated row in governed tables is missing either field.

---

## 4. Functional requirements

### 4.1 Data acquisition

- **FR-DA-1:** Connectors SHALL fetch judgment documents only from an **allowlisted** set of official Supreme Court of Victoria URLs.
- **FR-DA-2:** Downloads SHALL use retries with exponential backoff and SHALL record HTTP status, final URL, and download timestamp.
- **FR-DA-3:** Each artifact SHALL have a stable content checksum (e.g. SHA-256) and SHALL be deduplicated on checksum + canonical source id.
- **FR-DA-4:** An **ingestion manifest** SHALL list source URL, retrieval time, checksum, processing status, and error details if failed.

### 4.2 Processing and chunking

- **FR-DP-1:** Parsers SHALL support PDF and HTML as provided by official sources, with fallback strategy when primary parser fails (secondary parser or degraded text extraction), logged per artifact.
- **FR-DP-2:** Chunks SHALL carry provenance: source document id, URL, page or span reference where available, and chunk sequence.
- **FR-DP-3:** Chunking SHALL be legal-aware where possible (respect headings/sections; avoid arbitrary mid-sentence splits when feasible).
- **FR-DP-4:** Extracted metadata SHALL include at minimum: court, judgment date, case/docket identifier, jurisdiction (Victoria), and source URL.

### 4.3 Indexing

- **FR-IX-1:** Each chunk SHALL be embedded with a **cost-optimized** embedding model (configurable) and stored in pgvector with metadata linking to chunk and source document.
- **FR-IX-2:** The same chunk text (or normalized tokenization pipeline output) SHALL be indexed in OpenSearch for BM25 retrieval, with identical logical chunk id across stores.
- **FR-IX-3:** Upsert/update workflows SHALL be deterministic and repeatable (re-run produces consistent logical state; tombstones or version fields used where content is replaced).

### 4.4 Retrieval and ranking

- **FR-RT-1:** The retriever SHALL execute semantic `top-k` and keyword `top-k` **in parallel**.
- **FR-RT-2:** Results SHALL be fused via **RRF** (Reciprocal Rank Fusion) with documented default parameters; weights SHALL be configurable for tuning.
- **FR-RT-3:** Optional reranking (e.g. cross-encoder or LLM-based) MAY be enabled via configuration without breaking the baseline RRF path.

### 4.5 Generation and citations

- **FR-GN-1:** The LLM SHALL receive only retrieved chunk evidence (and metadata necessary for citation) in the prompt context window.
- **FR-GN-2:** Answers SHALL include **explicit citations** mapping statements to chunk ids and source references (URL + page/span where available).
- **FR-GN-3:** When evidence is insufficient, the system SHALL return a **no-answer or partial-answer** response with explanation and SHALL NOT fabricate citations.
- **FR-GN-4:** Post-generation validation SHALL detect citation ids that are not in the retrieved set and trigger repair or safe fallback (e.g. strip uncited claims or return error).

### 4.6 Serving API

- **FR-API-1:** `POST /query` (or equivalent) SHALL accept a user question and return answer text, citations, and confidence or evidence-sufficiency indicator.
- **FR-API-2:** `GET /health` (liveness/readiness) SHALL reflect dependency health (DB, OpenSearch, optional object store).
- **FR-API-3:** `POST /debug/retrieve` SHALL return fused candidate chunks and scores for tuning (protected in production).

### 4.7 Operations

- **FR-OP-1:** Idempotent ingestion and reindex commands SHALL exist for operators (CLI or admin API).
- **FR-OP-2:** Structured logs SHALL include correlation/request id, pipeline stage, and work item or job id.
- **FR-OP-3:** Audit logs SHALL record query events (subject to privacy policy), retrieval snapshot ids, and model versions used.

---

## 5. Non-functional requirements

### 5.1 Latency

- **NFR-LAT-1:** Under nominal load, **P50** end-to-end query latency SHOULD be suitable for interactive use; **P95** SHOULD remain bounded when OpenSearch and pgvector are healthy (exact targets to be set in `plan.md` after baseline benchmarks; initial build targets: P50 &lt; 5s, P95 &lt; 15s for MVP excluding cold start).
- **NFR-LAT-2:** Retrieval subsystems SHOULD complete within a configurable deadline; partial results or graceful degradation MUST be defined if a subsystem times out.

### 5.2 Reliability

- **NFR-REL-1:** Ingestion SHALL retry transient failures; permanent failures SHALL be recorded in the manifest without silent loss.
- **NFR-REL-2:** Index updates SHALL not leave orphaned references without a detectable state (e.g. explicit `pending`, `ready`, `failed`).

### 5.3 Security

- **NFR-SEC-1:** Secrets (API keys, DB credentials) SHALL be injected via environment or secret manager; never committed to the repository.
- **NFR-SEC-2:** Production deployments SHALL enforce TLS for external endpoints and authenticated access to debug/admin routes.
- **NFR-SEC-3:** Rate limiting SHOULD protect public query endpoints.

### 5.4 Auditability and compliance posture

- **NFR-AUD-1:** Every governed record SHALL satisfy the metadata policy (`system_user`, `update_time`).
- **NFR-AUD-2:** Source allowlist and corpus version SHALL be logged per answer for traceability.
- **NFR-AUD-3:** Redaction hooks MAY be applied to logged prompts/responses per organizational policy.

### 5.5 Observability

- **NFR-OBS-1:** Metrics SHOULD cover ingestion throughput, indexer lag, retrieval latency, fusion sizes, LLM token usage, and error rates.
- **NFR-OBS-2:** Distributed tracing SHOULD span API → retrieval → LLM where supported.

### 5.6 Cost

- **NFR-COST-1:** Default embedding and chat models SHALL be **cost-optimized** while meeting minimum quality gates on the offline eval set.

---

## 6. Data requirements and lineage

- **DR-1:** Raw artifacts immutable after first successful store (new versions create new rows/versions with lineage pointers).
- **DR-2:** Lineage graph: `source URL → raw artifact → parsed document → chunk → index records (OpenSearch + pgvector) → answer citation`.
- **DR-3:** Checksums and parser version identifiers SHALL be stored for reproducibility.

---

## 7. Compliance constraints and citation guarantees

- **CC-1:** Content source restriction: official Supreme Court of Victoria judgment publications only for MVP corpus.
- **CC-2:** No guarantee of legal correctness; UI and API documentation SHALL state limitations.
- **CC-3:** Citation guarantee: every factual claim in a generated answer MUST either cite retrieved chunk ids present in the current retrieval set or be omitted; validation enforces this invariant.

---

## 8. Acceptance criteria (requirements phase)

- Requirements are **testable** (each FR/NFR maps to verification in `tasks.md` / test plans).
- Corpus boundaries, retrieval behavior, citation rules, and metadata policy are **unambiguous**.
- Out-of-scope items are explicit to prevent scope creep.

---

## 9. Risks (summary)

| Risk                         | Mitigation |
|-----------------------------|------------|
| Source format variability   | Multi-parser fallback, validation, logging |
| Citation mismatch / hallucination | Strict context-only prompting, citation validation |
| Hybrid tuning complexity    | Offline eval set, configurable RRF/reranker |
| Compliance / privacy        | Allowlist, audit logs, redaction hooks |

---

## 10. Approval

**Approved for execution:** Yes (auto-approved per project instruction).  
**Next step:** Implement scaffold and pipelines per `plan.md` and `tasks.md`.
