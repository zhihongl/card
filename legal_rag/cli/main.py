from __future__ import annotations

import argparse
import logging
import os
import sys

from legal_rag.config import get_settings
from legal_rag.indexing.sync import sync_all_indexes
from legal_rag.ingestion.pipeline import ingest_all

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def cmd_ingest(args: argparse.Namespace) -> int:
    settings = get_settings()
    system_user = os.environ.get("LEGAL_RAG_SYSTEM_USER", "cli:ingest")
    manifest, chunks = ingest_all(settings, system_user=system_user)
    ok = sum(1 for m in manifest if m.status == "success")
    logger.info("Ingest finished: %s success / %s total, %s chunks", ok, len(manifest), len(chunks))
    if args.sync_index:
        sync_all_indexes(chunks, settings)
        logger.info("Index sync complete (where services configured).")
    return 0 if ok else 1


def cmd_serve(args: argparse.Namespace) -> int:
    import uvicorn

    uvicorn.run(
        "legal_rag.api.app:app",
        host=args.host,
        port=args.port,
        factory=False,
        reload=False,
    )
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m legal_rag")
    sub = parser.add_subparsers(dest="cmd", required=True)

    ingest_p = sub.add_parser("ingest", help="Crawl official listing, download, parse, chunk")
    ingest_p.add_argument(
        "--sync-index",
        action="store_true",
        help="After ingest, upsert into OpenSearch / pgvector when URLs are set",
    )
    ingest_p.set_defaults(func=cmd_ingest)

    serve_p = sub.add_parser("serve", help="Run FastAPI service")
    serve_p.add_argument("--host", default="0.0.0.0")
    serve_p.add_argument("--port", type=int, default=8000)
    serve_p.set_defaults(func=cmd_serve)

    args = parser.parse_args()
    code = args.func(args)
    if code:
        sys.exit(code)


if __name__ == "__main__":
    main()
