from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document

from app.rag.ingestion import run_ingestion

_INGESTION_MOD = "app.rag.ingestion"


@pytest.fixture
def mock_settings():
    with patch(f"{_INGESTION_MOD}.get_settings") as patched:
        settings = MagicMock()
        settings.qdrant_host = "test-host"
        settings.qdrant_port = 9999
        settings.qdrant_collection = "test_collection"
        patched.return_value = settings
        yield settings


def _fake_docs():
    return [Document(page_content="Irish text A"), Document(page_content="Irish text B")]


def _fake_chunks():
    return [
        Document(page_content="chunk 1"),
        Document(page_content="chunk 2"),
        Document(page_content="chunk 3"),
    ]


@pytest.fixture
def deps(mock_settings):
    """Patch all external dependencies for run_ingestion with sensible defaults."""
    with patch(f"{_INGESTION_MOD}.DirectoryLoader") as MockLoader, \
         patch(f"{_INGESTION_MOD}.RecursiveCharacterTextSplitter") as MockSplitter, \
         patch(f"{_INGESTION_MOD}.QdrantVectorStore") as MockQdrant, \
         patch(f"{_INGESTION_MOD}.get_embedder") as mock_embedder:

        MockLoader.return_value.load.return_value = _fake_docs()
        MockSplitter.return_value.split_documents.return_value = _fake_chunks()
        mock_embedder.return_value = MagicMock(name="embedder")

        yield SimpleNamespace(
            settings=mock_settings,
            Loader=MockLoader,
            Splitter=MockSplitter,
            Qdrant=MockQdrant,
            embedder=mock_embedder,
        )


class TestRunIngestion:
    def test_returns_chunk_count(self, deps):
        result = run_ingestion()

        assert result == len(_fake_chunks())

    def test_returns_zero_when_no_documents(self, deps):
        deps.Loader.return_value.load.return_value = []
        deps.Splitter.return_value.split_documents.return_value = []

        result = run_ingestion()

        assert result == 0

    def test_loads_txt_files_via_glob(self, deps):
        """DirectoryLoader is initialised with the glob pattern for .txt files."""
        run_ingestion()

        kwargs = deps.Loader.call_args.kwargs
        assert kwargs.get("glob") == "**/*.txt"

    def test_loads_txt_files_with_text_loader_cls(self, deps):
        """DirectoryLoader is initialised with TextLoader as the loader class."""
        run_ingestion()

        kwargs = deps.Loader.call_args.kwargs
        assert kwargs.get("loader_cls") is TextLoader

    def test_splits_with_correct_chunk_size_and_overlap(self, deps):
        run_ingestion()

        deps.Splitter.assert_called_once_with(chunk_size=500, chunk_overlap=50)

    def test_upserts_chunks_to_qdrant(self, deps):
        """QdrantVectorStore.from_documents receives the split chunks."""
        chunks = _fake_chunks()
        deps.Splitter.return_value.split_documents.return_value = chunks

        run_ingestion()

        call_kwargs = deps.Qdrant.from_documents.call_args.kwargs
        assert call_kwargs["documents"] == chunks

    def test_upserts_to_correct_collection(self, deps):
        run_ingestion()

        call_kwargs = deps.Qdrant.from_documents.call_args.kwargs
        assert call_kwargs["collection_name"] == deps.settings.qdrant_collection

    def test_connects_to_correct_qdrant_url(self, deps):
        """QdrantVectorStore receives a URL built from settings host and port."""
        run_ingestion()

        call_kwargs = deps.Qdrant.from_documents.call_args.kwargs
        expected = f"http://{deps.settings.qdrant_host}:{deps.settings.qdrant_port}"
        assert call_kwargs["url"] == expected

    def test_passes_embedder_to_qdrant(self, deps):
        """The cached embedder instance is forwarded to QdrantVectorStore."""
        run_ingestion()

        call_kwargs = deps.Qdrant.from_documents.call_args.kwargs
        assert call_kwargs["embedding"] is deps.embedder.return_value

    def test_raises_when_loader_fails(self, deps):
        deps.Loader.return_value.load.side_effect = OSError("directory not found")

        with pytest.raises(OSError):
            run_ingestion()

    def test_raises_when_qdrant_unavailable(self, deps):
        deps.Qdrant.from_documents.side_effect = ConnectionError("qdrant unreachable")

        with pytest.raises(ConnectionError):
            run_ingestion()
