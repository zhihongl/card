# WI-000001 — Implementation Plan: Legal RAG (Production-Oriented)

**Status:** Approved (auto-approved)  
**Work item:** WI-000001  
**Branch context:** `j00/legal-rag-requirements-c83b`

---

## 1. Goals

Deliver a production-oriented Legal RAG platform for ~50 Victorian Supreme Court judgments with hybrid retrieval, grounded answers, mandatory record metadata (`system_user`, `update_time`), and operational readiness.

---

## 2. Phases and outcomes

| Phase | Name | Outcome |
|-------|------|---------|
| 1 | Requirement definition | `requirements.md`, `spec.md`, `plan.md`, `tasks.md` (this package) |
| 2 | Project bootstrap | Runnable repo layout, deps, lint/format/typecheck, CI baseline |
| 3 | Legal data ingestion | 50 documents, manifest, checksums, no duplicates |
| 4 | Parsing, chunking, enrichment | Chunks with provenance and extracted metadata |
| 5 | Hybrid indexing | Parity: each chunk in pgvector + OpenSearch; deterministic upsert |
| 6 | Retrieval + RAG service | RRF fusion, citations, insufficient-evidence behavior |
| 7 | Quality, security, operations | Observability, auth model for admin/debug, runbooks, deployment manifests |

---

## 3. Repository layout (target)

Planned structure (to be created in Phase 2; may coexist with existing legacy code until explicitly migrated):

```
AllocationsManagement.Content/specs/...
src/                    # application packages (language TBD in bootstrap)
tests/                  # unit + integration + e2e
infra/                  # IaC, docker-compose, OpenSearch/Postgres bootstrap
docs/                   # architecture notes, ADRs (minimal; avoid unsolicited README sprawl)
scripts/                # ingest, reindex, eval helpers
```

---

## 4. Architecture decisions (fixed for MVP)

- **Keyword index:** OpenSearch BM25.
- **Semantic index:** PostgreSQL pgvector.
- **Fusion:** RRF; optional rerank behind feature flag.
- **LLM:** OpenAI (cost-optimized defaults).
- **Corpus:** Published judgments only; official Victoria Supreme Court sources; allowlisted URLs.

---

## 5. Metadata enforcement

- Schema migrations and ORM/DAL layers include **NOT NULL** or equivalent application-level validation for `system_user` and `update_time` on all governed tables.
- Shared helper for “touch” on update ensures consistent UTC timestamps.
- CI test suite includes **metadata policy tests** for create/update paths.

---

## 6. Testing strategy (summary)

- **Unit:** parsers, chunk boundaries, RRF determinism, citation validator, metadata policy.
- **Integration:** sample ingestion, dual-index write/read parity, retrieval → generation with mocked or recorded LLM where appropriate.
- **E2E / acceptance:** fact lookup, precedent-like similarity, insufficient-evidence queries.
- **Non-functional:** latency percentiles, concurrency smoke, fault injection (source down, OpenSearch down).

---

## 7. Security and compliance (MVP baseline)

- Secret management via environment; rotate keys in runbook.
- TLS termination at ingress; authenticate `/debug/*` and operator commands.
- Audit logging for queries with configurable PII policy (hash questions in logs by default).

---

## 8. Observability

- Structured JSON logs with `trace_id`, `chunk_count`, `fusion_params`, model ids.
- Metrics: ingestion success/fail, index lag, retrieval latency histograms, LLM token usage, validation failures.

---

## 9. Dependencies and environments

- Local: Docker Compose for Postgres (pgvector) + OpenSearch.
- CI: ephemeral services or contract tests with mocks (documented in Phase 2).

---

## 10. Definition of done (program level)

- All phases’ acceptance criteria in `tasks.md` satisfied.
- Offline eval thresholds met or explicitly waived with documented rationale in ADR.
- Runbook covers ingest, reindex, rollback, and incident response for index corruption.

---

## 11. Plan approval

**Approved:** Yes (auto-approved).  
**Owner:** Engineering (Legal RAG workstream).
