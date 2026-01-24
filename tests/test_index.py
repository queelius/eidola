"""Tests for RAG index.

Note: These tests require sentence-transformers and faiss-cpu.
They are skipped if these dependencies are not available.
"""

import pytest
from pathlib import Path
from typing import List

try:
    import faiss
    import numpy as np

    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

from longshade.models import Chunk, Conversation


pytestmark = pytest.mark.skipif(not HAS_FAISS, reason="faiss-cpu not installed")


@pytest.fixture
def sample_chunks() -> List[Chunk]:
    """Create sample chunks with mock embeddings."""
    chunks = [
        Chunk(
            id="chunk-1",
            text="Functional programming emphasizes immutability",
            source="conversation",
            conversation_id="conv-001",
            turn_index=0,
            total_turns=2,
            metadata={"message_index": 0},
        ),
        Chunk(
            id="chunk-2",
            text="Category theory provides abstract structure",
            source="conversation",
            conversation_id="conv-001",
            turn_index=1,
            total_turns=2,
            metadata={"message_index": 2},
        ),
        Chunk(
            id="chunk-3",
            text="Durability in software is about conceptual clarity",
            source="writing",
        ),
    ]

    # Add mock embeddings (384-dim like MiniLM)
    for chunk in chunks:
        chunk.embedding = np.random.randn(384).astype(np.float32)

    return chunks


class TestRAGIndex:
    """Tests for RAGIndex class."""

    def test_add_chunks(self, sample_chunks: List[Chunk]) -> None:
        """Test adding chunks to index."""
        from longshade.rag import RAGIndex

        index = RAGIndex(embedding_dim=384)
        index.add_chunks(sample_chunks)

        assert len(index) == 3

    def test_save_and_load(self, sample_chunks: List[Chunk], tmp_path: Path) -> None:
        """Test saving and loading index."""
        from longshade.rag import RAGIndex

        # Create and save
        index = RAGIndex(embedding_dim=384)
        index.add_chunks(sample_chunks)
        index.save(tmp_path / "rag")

        # Verify files created
        assert (tmp_path / "rag" / "index.faiss").exists()
        assert (tmp_path / "rag" / "chunks.jsonl").exists()
        assert (tmp_path / "rag" / "metadata.json").exists()

        # Load and verify
        loaded = RAGIndex.load(tmp_path / "rag")
        assert len(loaded) == 3

    def test_search_basic(self, sample_chunks: List[Chunk]) -> None:
        """Test basic search functionality.

        Note: This test uses mock embeddings, so results are not meaningful.
        It just verifies the search pipeline works.
        """
        from longshade.rag import RAGIndex, Embedder

        # Create a mock embedder that returns consistent embeddings
        class MockEmbedder:
            model_name = "mock"
            embedding_dim = 384

            def embed(self, text):
                # Return first chunk's embedding for deterministic results
                return sample_chunks[0].embedding

        index = RAGIndex(embedding_dim=384)
        index.embedder = MockEmbedder()
        index.add_chunks(sample_chunks)

        results = index.search("functional programming", k=2, expand_context=False)

        assert len(results) <= 2
        assert all("chunk" in r and "score" in r for r in results)

    def test_conversation_context_stored(
        self, sample_chunks: List[Chunk], sample_conversation: Conversation
    ) -> None:
        """Test that conversations are stored for context expansion."""
        from longshade.rag import RAGIndex

        index = RAGIndex(embedding_dim=384)
        index.add_chunks(sample_chunks)
        index.add_conversations([sample_conversation])

        assert sample_conversation.id in index._conversations

    def test_metadata_includes_model_info(
        self, sample_chunks: List[Chunk], tmp_path: Path
    ) -> None:
        """Test that saved metadata includes model information."""
        import json
        from longshade.rag import RAGIndex

        index = RAGIndex(embedding_dim=384)
        index.add_chunks(sample_chunks)
        index.save(tmp_path / "rag")

        with open(tmp_path / "rag" / "metadata.json") as f:
            metadata = json.load(f)

        assert "embedding_model" in metadata
        assert "embedding_dim" in metadata
        assert metadata["total_chunks"] == 3

    def test_empty_chunks_handled(self) -> None:
        """Test that empty chunk list is handled."""
        from longshade.rag import RAGIndex

        index = RAGIndex(embedding_dim=384)
        index.add_chunks([])

        assert len(index) == 0
