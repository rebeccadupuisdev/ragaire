from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_run_ingestion():
    with patch("app.api.routes.run_ingestion", return_value=42) as m:
        yield m


@pytest.fixture
def mock_run_query():
    with patch("app.api.routes.run_query") as m:
        m.return_value = {
            "answer": "Dia duit means hello.",
            "sources": ["chunk A", "chunk B"],
        }
        yield m


@pytest.fixture
def mock_get_client():
    with patch("app.api.routes.get_client") as m:
        m.return_value = MagicMock()
        yield m


# ---------------------------------------------------------------------------
# POST /ingest
# ---------------------------------------------------------------------------

class TestIngest:
    def test_returns_200(self, mock_run_ingestion):
        response = client.post("/ingest")
        assert response.status_code == 200

    def test_response_schema(self, mock_run_ingestion):
        data = client.post("/ingest").json()
        assert data["status"] == "ok"
        assert data["chunks_indexed"] == 42

    def test_calls_run_ingestion_once(self, mock_run_ingestion):
        client.post("/ingest")
        mock_run_ingestion.assert_called_once()

    def test_raises_when_run_ingestion_fails(self):
        with patch("app.api.routes.run_ingestion", side_effect=OSError("disk full")):
            with pytest.raises(OSError, match="disk full"):
                client.post("/ingest")


# ---------------------------------------------------------------------------
# POST /query
# ---------------------------------------------------------------------------

class TestQuery:
    def test_returns_200(self, mock_run_query):
        response = client.post("/query", json={"question": "What is dia duit?"})
        assert response.status_code == 200

    def test_response_schema(self, mock_run_query):
        data = client.post("/query", json={"question": "What is dia duit?"}).json()
        assert data["answer"] == "Dia duit means hello."
        assert data["sources"] == ["chunk A", "chunk B"]

    def test_default_top_k(self, mock_run_query):
        client.post("/query", json={"question": "Test?"})
        _, kwargs = mock_run_query.call_args
        assert kwargs["top_k"] == 4

    def test_custom_top_k(self, mock_run_query):
        client.post("/query", json={"question": "Test?", "top_k": 8})
        _, kwargs = mock_run_query.call_args
        assert kwargs["top_k"] == 8

    def test_question_forwarded(self, mock_run_query):
        client.post("/query", json={"question": "Cad is ainm duit?"})
        call_args = mock_run_query.call_args
        question = call_args.args[0] if call_args.args else call_args.kwargs.get("question")
        assert question == "Cad is ainm duit?"

    def test_missing_question_returns_422(self, mock_run_query):
        response = client.post("/query", json={})
        assert response.status_code == 422

    def test_top_k_zero_returns_422(self, mock_run_query):
        response = client.post("/query", json={"question": "Test?", "top_k": 0})
        assert response.status_code == 422

    def test_top_k_negative_returns_422(self, mock_run_query):
        response = client.post("/query", json={"question": "Test?", "top_k": -1})
        assert response.status_code == 422

    def test_raises_when_run_query_fails(self):
        with patch("app.api.routes.run_query", side_effect=RuntimeError("LLM down")):
            with pytest.raises(RuntimeError, match="LLM down"):
                client.post("/query", json={"question": "Test?"})


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

class TestHealth:
    def test_returns_200(self, mock_get_client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_connected_when_qdrant_reachable(self, mock_get_client):
        data = client.get("/health").json()
        assert data["status"] == "healthy"
        assert data["vector_store"] == "connected"

    def test_unavailable_when_qdrant_raises(self):
        with patch("app.api.routes.get_client", side_effect=Exception("unreachable")):
            data = client.get("/health").json()
        assert data["status"] == "healthy"
        assert data["vector_store"] == "unavailable"
