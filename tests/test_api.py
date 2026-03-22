from fastapi.testclient import TestClient

from legal_rag.api.app import app


def test_health_endpoint() -> None:
    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] in ("ok", "degraded")
        assert "postgres" in data
        assert "opensearch" in data


def test_query_smoke() -> None:
    with TestClient(app) as client:
        r = client.post("/query", json={"question": "What is a judgment?"})
        assert r.status_code == 200
        body = r.json()
        assert "answer" in body
        assert "citations" in body
        assert "retrieval_trace_id" in body
