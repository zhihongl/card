from legal_rag.chunking import chunk_document, new_document_id
from legal_rag.metadata import utc_now
from legal_rag.models import SourceDocument


def test_chunk_document_splits_and_metadata() -> None:
    doc = SourceDocument(
        system_user="test",
        update_time=utc_now(),
        document_id=new_document_id("https://example.invalid/case"),
        source_url="https://example.invalid/case",
        format="html",
        checksum_sha256="0" * 64,
        raw_storage_path="/tmp/x",
    )
    text = "Para one.\n\nPara two is longer " + ("word " * 400)
    chunks = chunk_document(doc, text, system_user="test:chunk")
    assert chunks
    assert all(c.system_user == "test:chunk" for c in chunks)
    assert all(c.update_time.tzinfo is not None for c in chunks)
    assert {c.document_id for c in chunks} == {doc.document_id}
