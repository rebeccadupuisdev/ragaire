from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage

from app.rag.pipeline import run_query

_PIPELINE_MOD = "app.rag.pipeline"

_FAKE_CHUNKS = [
    Document(page_content="Irish follows VSO word order."),
    Document(page_content="The copula 'is' links subject to predicate."),
]
_FAKE_ANSWER = "Irish uses VSO word order, unlike English."
_FAKE_QUESTION = "What is VSO order?"


@pytest.fixture(autouse=True)
def mock_embedder():
    """Patch get_embedder in the pipeline module so no Cohere API key is needed."""
    with patch(f"{_PIPELINE_MOD}.get_embedder") as patched:
        patched.return_value = MagicMock()
        yield patched


@pytest.fixture
def mock_settings():
    with patch(f"{_PIPELINE_MOD}.get_settings") as patched:
        settings = MagicMock()
        settings.qdrant_host = "test-host"
        settings.qdrant_port = 9999
        settings.qdrant_collection = "test_collection"
        patched.return_value = settings
        yield settings


@pytest.fixture
def mock_vector_store():
    """Patch QdrantVectorStore so retrieval returns _FAKE_CHUNKS."""
    with patch(f"{_PIPELINE_MOD}.QdrantVectorStore") as MockQdrant:
        mock_store = MagicMock()
        mock_retriever = MagicMock()
        mock_retriever.invoke.return_value = _FAKE_CHUNKS
        mock_store.as_retriever.return_value = mock_retriever
        MockQdrant.from_existing_collection.return_value = mock_store
        yield MockQdrant


@pytest.fixture
def mock_llm():
    """Patch ChatAnthropic so invoke returns a response with _FAKE_ANSWER."""
    with patch(f"{_PIPELINE_MOD}.ChatAnthropic") as MockLLM:
        mock_response = MagicMock()
        mock_response.content = _FAKE_ANSWER
        MockLLM.return_value.invoke.return_value = mock_response
        yield MockLLM


@pytest.fixture
def deps(mock_settings, mock_vector_store, mock_llm):
    """Combine all pipeline mocks into a single namespace."""
    mock_store = mock_vector_store.from_existing_collection.return_value
    yield SimpleNamespace(
        settings=mock_settings,
        Qdrant=mock_vector_store,
        store=mock_store,
        retriever=mock_store.as_retriever.return_value,
        LLM=mock_llm,
        llm_instance=mock_llm.return_value,
    )


class TestRunQuery:
    def test_returns_answer_key(self, deps):
        result = run_query(_FAKE_QUESTION)

        assert "answer" in result

    def test_returns_sources_key(self, deps):
        result = run_query(_FAKE_QUESTION)

        assert "sources" in result

    def test_answer_matches_llm_response(self, deps):
        """The 'answer' value is the content returned by the LLM."""
        result = run_query(_FAKE_QUESTION)

        assert result["answer"] == _FAKE_ANSWER

    def test_sources_match_retrieved_chunk_contents(self, deps):
        """The 'sources' value is a list of page_content strings from retrieved docs."""
        result = run_query(_FAKE_QUESTION)

        expected = [doc.page_content for doc in _FAKE_CHUNKS]
        assert result["sources"] == expected

    def test_returns_empty_sources_when_no_chunks_retrieved(self, deps):
        deps.retriever.invoke.return_value = []

        result = run_query(_FAKE_QUESTION)

        assert result["sources"] == []

    def test_retriever_called_with_top_k(self, deps):
        """as_retriever is called with the top_k value passed to run_query."""
        run_query(_FAKE_QUESTION, top_k=6)

        deps.store.as_retriever.assert_called_once_with(search_kwargs={"k": 6})

    def test_uses_default_top_k_of_4(self, deps):
        """run_query defaults to top_k=4 when no value is provided."""
        run_query(_FAKE_QUESTION)

        deps.store.as_retriever.assert_called_once_with(search_kwargs={"k": 4})

    def test_retriever_invoked_with_question(self, deps):
        """retriever.invoke is called with the exact question string."""
        run_query(_FAKE_QUESTION)

        deps.retriever.invoke.assert_called_once_with(_FAKE_QUESTION)

    def test_connects_to_correct_qdrant_collection(self, deps):
        run_query(_FAKE_QUESTION)

        call_kwargs = deps.Qdrant.from_existing_collection.call_args.kwargs
        assert call_kwargs["collection_name"] == deps.settings.qdrant_collection

    def test_connects_to_correct_qdrant_url(self, deps):
        run_query(_FAKE_QUESTION)

        call_kwargs = deps.Qdrant.from_existing_collection.call_args.kwargs
        expected = f"http://{deps.settings.qdrant_host}:{deps.settings.qdrant_port}"
        assert call_kwargs["url"] == expected

    def test_llm_receives_all_retrieved_chunks_in_context(self, deps):
        """Every retrieved chunk appears in the messages sent to the LLM."""
        run_query(_FAKE_QUESTION)

        messages = deps.llm_instance.invoke.call_args.args[0]
        combined = " ".join(m.content for m in messages)
        for chunk in _FAKE_CHUNKS:
            assert chunk.page_content in combined

    def test_llm_receives_question_in_messages(self, deps):
        """The question string appears in the messages sent to the LLM."""
        run_query(_FAKE_QUESTION)

        messages = deps.llm_instance.invoke.call_args.args[0]
        combined = " ".join(m.content for m in messages)
        assert _FAKE_QUESTION in combined

    def test_llm_receives_system_prompt(self, deps):
        """A SystemMessage is the first message sent to the LLM."""
        run_query(_FAKE_QUESTION)

        messages = deps.llm_instance.invoke.call_args.args[0]
        assert isinstance(messages[0], SystemMessage)

    def test_uses_correct_anthropic_model(self, deps):
        run_query(_FAKE_QUESTION)

        deps.LLM.assert_called_once_with(model="claude-haiku-4-5-20251001")

    def test_raises_when_llm_fails(self, deps):
        deps.llm_instance.invoke.side_effect = RuntimeError("LLM unavailable")

        with pytest.raises(RuntimeError):
            run_query(_FAKE_QUESTION)

    def test_raises_when_retrieval_fails(self, deps):
        deps.retriever.invoke.side_effect = ConnectionError("qdrant unreachable")

        with pytest.raises(ConnectionError):
            run_query(_FAKE_QUESTION)
