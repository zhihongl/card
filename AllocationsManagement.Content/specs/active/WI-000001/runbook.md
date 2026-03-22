# WI-000001 — Operations runbook (MVP)

## Local dependencies

- Java + Maven (legacy fraud-detection module)
- Python 3.11+
- Docker (optional, for OpenSearch + Postgres/pgvector)

## Install

```bash
pip install -r requirements.txt
bash scripts/cloud-setup.sh
```

## Ingest official judgments (Supreme Court of Victoria)

Uses the public judgments listing with pagination until `MAX_INGEST_DOCUMENTS` (default 50).

```bash
export LEGAL_RAG_SYSTEM_USER="your-id-or-service"
python -m legal_rag ingest
```

Artifacts:

- `data/raw/` — downloaded bytes (checksum-named)
- `data/processed/manifest.jsonl` — per-URL status, checksum, `system_user`, `update_time`
- `data/processed/chunks.jsonl` — chunk records for the API

## Hybrid index (optional)

1. Start services:

```bash
docker compose -f infra/docker-compose.yml up -d
```

2. Configure URLs:

```bash
export DATABASE_URL=postgresql://legalrag:legalrag@localhost:5432/legalrag
export OPENSEARCH_URL=http://localhost:9200
```

3. Ingest + sync:

```bash
python -m legal_rag ingest --sync-index
```

Note: pgvector table is recreated on each sync to match embedding dimension (mock vs OpenAI).

## Run API

```bash
export LEGAL_RAG_CHUNKS_PATH=data/processed/chunks.jsonl   # optional override
python -m legal_rag serve --port 8000
```

Endpoints: `GET /health`, `POST /query`, `POST /debug/retrieve`.

## OpenAI (optional)

```bash
export OPENAI_API_KEY=...
export OPENAI_CHAT_MODEL=gpt-4o-mini
export OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

Without `OPENAI_API_KEY`, retrieval still runs with deterministic mock embeddings; `/query` returns excerpt mode (degraded).

## Reindex / reingest

- Re-run `python -m legal_rag ingest` (idempotent raw files by checksum).
- Re-run with `--sync-index` after services are healthy.

## Security notes

- Do not commit `.env` or API keys.
- Protect `/debug/retrieve` behind auth in production (not implemented in MVP scaffold).
