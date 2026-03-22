from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from legal_rag.config import Settings
from legal_rag.embedding import embed_documents
from legal_rag.models import ChunkRecord


def _os_client(settings: Settings) -> Any:
    from opensearchpy import OpenSearch

    parsed = urlparse(settings.opensearch_url or "http://localhost:9200")
    host = parsed.hostname or "localhost"
    port = parsed.port or (443 if parsed.scheme == "https" else 9200)
    use_ssl = parsed.scheme == "https"
    return OpenSearch(
        hosts=[{"host": host, "port": port}],
        use_ssl=use_ssl,
        verify_certs=False,
        ssl_show_warn=False,
    )


def sync_opensearch(chunks: list[ChunkRecord], settings: Settings) -> None:
    if not settings.opensearch_url or not chunks:
        return
    from opensearchpy.helpers import bulk

    client = _os_client(settings)
    index = settings.opensearch_index
    if not client.indices.exists(index=index):
        client.indices.create(
            index=index,
            body={
                "mappings": {
                    "properties": {
                        "chunk_id": {"type": "keyword"},
                        "document_id": {"type": "keyword"},
                        "source_url": {"type": "keyword"},
                        "text": {"type": "text"},
                        "sequence": {"type": "integer"},
                    }
                }
            },
        )
    actions = [
        {
            "_op_type": "index",
            "_index": index,
            "_id": c.chunk_id,
            "_source": {
                "chunk_id": c.chunk_id,
                "document_id": c.document_id,
                "source_url": c.source_url,
                "text": c.text,
                "sequence": c.sequence,
            },
        }
        for c in chunks
    ]
    bulk(client, actions)


def sync_pgvector(chunks: list[ChunkRecord], settings: Settings) -> None:
    if not settings.database_url or not chunks:
        return
    import psycopg

    texts = [c.text[:8000] for c in chunks]
    vectors = embed_documents(texts, settings)
    dim = len(vectors[0])
    with psycopg.connect(settings.database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute("DROP TABLE IF EXISTS legal_chunks;")
            cur.execute(
                f"""
                CREATE TABLE legal_chunks (
                  chunk_id TEXT PRIMARY KEY,
                  document_id TEXT NOT NULL,
                  source_url TEXT NOT NULL,
                  sequence INT NOT NULL,
                  text TEXT NOT NULL,
                  embedding vector({dim}) NOT NULL,
                  system_user TEXT NOT NULL,
                  update_time TIMESTAMPTZ NOT NULL
                );
                """
            )
            for c, vec in zip(chunks, vectors, strict=True):
                literal = "[" + ",".join(str(float(x)) for x in vec) + "]"
                cur.execute(
                    """
                    INSERT INTO legal_chunks (
                      chunk_id, document_id, source_url, sequence, text, embedding,
                      system_user, update_time
                    ) VALUES (%s, %s, %s, %s, %s, %s::vector, %s, %s)
                    """,
                    (
                        c.chunk_id,
                        c.document_id,
                        c.source_url,
                        c.sequence,
                        c.text,
                        literal,
                        c.system_user,
                        c.update_time,
                    ),
                )
        conn.commit()


def sync_all_indexes(chunks: list[ChunkRecord], settings: Settings) -> None:
    sync_opensearch(chunks, settings)
    sync_pgvector(chunks, settings)
