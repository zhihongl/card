# WI-000001 — Task Breakdown and Verification

**Status:** Approved (auto-approved)  
**Related:** `requirements.md`, `spec.md`, `plan.md`

---

## Phase 1 — Requirement definition ✅

| ID | Task | Done when |
|----|------|-----------|
| T1.1 | Draft `requirements.md` with FR/NFR, data lineage, compliance, metadata policy, acceptance criteria, out-of-scope | This file set reviewed and present in repo |
| T1.2 | Draft `spec.md` with APIs, data model, retrieval/generation behavior | Aligned with requirements; no unresolved contradictions |
| T1.3 | Draft `plan.md` with phases and repo layout | Execution order clear |
| T1.4 | Draft `tasks.md` with verifiable checklist | Each phase has measurable exit criteria |

**Verification:** Peer or automated checklist — every FR/NFR in `requirements.md` maps to at least one task or test in later phases.

---

## Phase 2 — Project bootstrap

| ID | Task | Done when |
|----|------|-----------|
| T2.1 | Create `src/`, `tests/`, `infra/`, `scripts/` (and minimal `docs/` if ADRs needed) | Directories exist; package manifests committed |
| T2.2 | Add dependency management (e.g. `pyproject.toml` / `requirements.txt` or existing Maven coexistence documented) | `install` documented; lockfile or equivalent |
| T2.3 | Configure formatter, linter, type checker | CI job runs clean on baseline |
| T2.4 | Add baseline unit test and CI pipeline | Green build on fresh clone |

**Verification:** New developer can clone, install, run lint/typecheck/tests per README or `docs/dev.md` (only if explicitly added in Phase 2).

---

## Phase 3 — Legal data ingestion

| ID | Task | Done when |
|----|------|-----------|
| T3.1 | Implement allowlisted Victoria Supreme Court connectors | Only official URLs accepted |
| T3.2 | Download with retry/backoff; record checksum, timestamps, `system_user`, `update_time` | Manifest + DB rows complete |
| T3.3 | Deduplicate on checksum + canonical id | No duplicate raw artifacts |
| T3.4 | Ingestion manifest export (CSV/JSON) for audit | 50 rows succeeded for MVP target |

**Verification:** Count(`status=success`) ≥ 50; zero duplicate checksums; each row has provenance fields.

---

## Phase 4 — Parsing, chunking, enrichment

| ID | Task | Done when |
|----|------|-----------|
| T4.1 | PDF/HTML parsers with fallback | Golden-file tests on sample judgments |
| T4.2 | Legal-aware chunking | Unit tests on heading boundaries |
| T4.3 | Metadata extraction (court, date, case id, URL) | Fields populated ≥ agreed threshold (e.g. 95% non-null) |
| T4.4 | Persist chunks with lineage to raw artifact | Trace query from chunk → source URL works |

**Verification:** Random sample: for 10 chunks, manual trace to correct page/span/section.

---

## Phase 5 — Hybrid indexing

| ID | Task | Done when |
|----|------|-----------|
| T5.1 | Embedding pipeline (cost-optimized model) + pgvector storage | All chunks embedded; metadata includes model id |
| T5.2 | OpenSearch indexing pipeline | All chunks searchable by unique phrase test |
| T5.3 | Synchronized upsert/reindex | Second run idempotent or versioned correctly |
| T5.4 | Metadata policy on index backing tables | Tests assert `system_user`, `update_time` |

**Verification:** For arbitrary chunk id, `exists_in_pgvector ∧ exists_in_opensearch`.

---

## Phase 6 — Hybrid retrieval + RAG service

| ID | Task | Done when |
|----|------|-----------|
| T6.1 | Parallel semantic + keyword retrieval | Latency logged per leg |
| T6.2 | RRF fusion (configurable) | Determinism unit tests |
| T6.3 | Optional reranker behind flag | Off by default; documented |
| T6.4 | OpenAI prompt with strict citations | Integration test with stubbed LLM or replay |
| T6.5 | Citation validator | Invalid chunk id → retry or safe response |
| T6.6 | `/query`, `/health`, `/debug/retrieve` | Contract tests |

**Verification:** E2E: answer cites only retrieved ids; insufficient-evidence scenario returns no fabricated citations.

---

## Phase 7 — Quality, security, operations

| ID | Task | Done when |
|----|------|-----------|
| T7.1 | Structured logging + metrics + tracing hooks | Dashboard or log queries documented |
| T7.2 | Rate limits and auth for debug/admin | Config toggles tested |
| T7.3 | Secret handling documented | No secrets in git; scan passes |
| T7.4 | Runbook: ingest, reindex, failure recovery | Operator can execute without code reading |
| T7.5 | Deployment manifests (e.g. K8s/Compose prod overlays) | Staging deploy succeeds |

**Verification:** Tabletop: simulate OpenSearch outage — system behavior matches runbook (degraded mode or clear error).

---

## Cross-cutting tests (references)

- **Metadata policy:** `tests/test_metadata_policy.py` (or equivalent) — assert all create/update paths set `system_user` and `update_time`.
- **RRF:** fixed input ranking → fixed fused order.
- **Citation validation:** LLM output with bogus id → caught.

---

## Work item completion

When Phases 1–7 acceptance criteria are met, move this folder from:

`AllocationsManagement.Content/specs/active/WI-000001/`

to:

`AllocationsManagement.Content/specs/done/WI-000001/`

---

## Tasks approval

**Approved:** Yes (auto-approved).
