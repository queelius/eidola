"""Tests for RAG chunker."""

import pytest
from typing import List

from longshade.models import Conversation, Writing, Email, Bookmark, Photo, Reading
from longshade.rag import Chunker, ChunkerConfig, chunk_conversations, chunk_writings


class TestChunker:
    """Tests for Chunker class."""

    def test_chunk_conversation(self, sample_conversation: Conversation) -> None:
        """Test chunking a conversation into turns."""
        chunker = Chunker()
        chunks = list(chunker.chunk_conversation(sample_conversation))

        # Should create one chunk per user message
        assert len(chunks) == 2

        # Check first chunk
        chunk = chunks[0]
        assert chunk.source == "conversation"
        assert chunk.conversation_id == "conv-001"
        assert chunk.turn_index == 0
        assert chunk.total_turns == 2
        assert "functional programming" in chunk.text.lower()

    def test_chunk_conversation_metadata(
        self, sample_conversation: Conversation
    ) -> None:
        """Test that conversation chunks have correct metadata."""
        chunker = Chunker()
        chunks = list(chunker.chunk_conversation(sample_conversation))

        for chunk in chunks:
            assert "message_index" in chunk.metadata
            assert chunk.conversation_id == sample_conversation.id

    def test_chunk_writing(self, sample_writing: Writing) -> None:
        """Test chunking a writing into paragraphs."""
        chunker = Chunker()
        chunks = list(chunker.chunk_writing(sample_writing))

        assert len(chunks) > 0
        assert all(c.source == "writing" for c in chunks)
        assert chunks[0].metadata.get("title") == sample_writing.title

    def test_chunk_writing_respects_size(self) -> None:
        """Test that chunks respect max size."""
        long_content = "A" * 1000 + "\n\n" + "B" * 1000
        writing = Writing(content=long_content, title="Long")

        chunker = Chunker(ChunkerConfig(chunk_size=500))
        chunks = list(chunker.chunk_writing(writing))

        # Should split into multiple chunks
        assert len(chunks) > 1

    def test_chunk_email(self, sample_email: Email) -> None:
        """Test chunking an email."""
        chunker = Chunker()
        chunks = list(chunker.chunk_email(sample_email))

        assert len(chunks) == 1
        chunk = chunks[0]
        assert chunk.source == "email"
        assert "Subject:" in chunk.text
        assert sample_email.subject in chunk.text

    def test_chunk_bookmark_with_annotation(self, sample_bookmark: Bookmark) -> None:
        """Test chunking a bookmark with annotation."""
        chunker = Chunker()
        chunks = list(chunker.chunk_bookmark(sample_bookmark))

        assert len(chunks) == 1
        assert chunks[0].source == "bookmark"
        assert chunks[0].text == sample_bookmark.annotation

    def test_chunk_bookmark_without_annotation(self) -> None:
        """Test that bookmarks without annotation yield nothing."""
        bookmark = Bookmark(url="https://example.com")

        chunker = Chunker()
        chunks = list(chunker.chunk_bookmark(bookmark))

        assert len(chunks) == 0

    def test_chunk_photo_with_caption(self, sample_photo: Photo) -> None:
        """Test chunking a photo with caption."""
        chunker = Chunker()
        chunks = list(chunker.chunk_photo(sample_photo))

        assert len(chunks) == 1
        assert chunks[0].source == "photo"
        assert chunks[0].text == sample_photo.caption

    def test_chunk_photo_without_caption(self) -> None:
        """Test that photos without caption yield nothing."""
        photo = Photo(path="2024/01/image.jpg")

        chunker = Chunker()
        chunks = list(chunker.chunk_photo(photo))

        assert len(chunks) == 0

    def test_chunk_reading_with_review(self, sample_reading: Reading) -> None:
        """Test chunking reading with review."""
        chunker = Chunker()
        chunks = list(chunker.chunk_reading(sample_reading))

        # Should have review chunk + highlight chunks
        assert len(chunks) >= 1

        review_chunks = [c for c in chunks if c.metadata.get("chunk_type") == "review"]
        assert len(review_chunks) == 1
        assert sample_reading.review in review_chunks[0].text

    def test_chunk_reading_highlights(self, sample_reading: Reading) -> None:
        """Test chunking reading highlights with notes."""
        chunker = Chunker()
        chunks = list(chunker.chunk_reading(sample_reading))

        highlight_chunks = [
            c for c in chunks if c.metadata.get("chunk_type") == "highlight"
        ]
        assert len(highlight_chunks) == 1

    def test_chunk_reading_no_review_no_notes(self) -> None:
        """Test reading without review or notes yields nothing."""
        reading = Reading(title="Empty Book")

        chunker = Chunker()
        chunks = list(chunker.chunk_reading(reading))

        assert len(chunks) == 0


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_chunk_conversations(self, sample_conversation: Conversation) -> None:
        """Test chunk_conversations helper."""
        chunks = chunk_conversations([sample_conversation])
        assert len(chunks) == 2
        assert all(c.source == "conversation" for c in chunks)

    def test_chunk_writings(self, sample_writing: Writing) -> None:
        """Test chunk_writings helper."""
        chunks = chunk_writings([sample_writing])
        assert len(chunks) > 0
        assert all(c.source == "writing" for c in chunks)


class TestChunkerConfig:
    """Tests for ChunkerConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = ChunkerConfig()
        assert config.context_turns == 3
        assert config.max_context_turns == 10
        assert config.chunk_size == 512
        assert config.chunk_overlap == 64

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = ChunkerConfig(
            context_turns=5,
            chunk_size=256,
        )
        assert config.context_turns == 5
        assert config.chunk_size == 256
