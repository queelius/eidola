"""Tests for data models."""

import pytest
from datetime import datetime

from longshade.models import (
    Message,
    Conversation,
    Chunk,
    Writing,
    Email,
    Bookmark,
    Photo,
    Reading,
    Highlight,
)


class TestMessage:
    """Tests for Message model."""

    def test_message_creation(self) -> None:
        """Test basic message creation."""
        msg = Message(role="user", content="Hello world")
        assert msg.role == "user"
        assert msg.content == "Hello world"
        assert msg.timestamp is None
        assert msg.source is None

    def test_message_with_all_fields(self) -> None:
        """Test message with all optional fields."""
        ts = datetime(2024, 1, 15, 10, 30, 0)
        msg = Message(
            role="user",
            content="Hello",
            timestamp=ts,
            source="ctk",
            conversation_id="conv-001",
            topic="greeting",
        )
        assert msg.timestamp == ts
        assert msg.source == "ctk"
        assert msg.conversation_id == "conv-001"
        assert msg.topic == "greeting"

    def test_message_invalid_role(self) -> None:
        """Test that invalid role raises error."""
        with pytest.raises(ValueError, match="Invalid role"):
            Message(role="invalid", content="Hello")

    def test_message_valid_roles(self) -> None:
        """Test all valid roles."""
        for role in ["user", "assistant", "system"]:
            msg = Message(role=role, content="Hello")
            assert msg.role == role


class TestConversation:
    """Tests for Conversation model."""

    def test_conversation_creation(self, sample_messages) -> None:
        """Test conversation creation."""
        conv = Conversation(id="conv-001", messages=sample_messages)
        assert conv.id == "conv-001"
        assert len(conv.messages) == 3

    def test_user_messages(self, sample_conversation) -> None:
        """Test user_messages property."""
        user_msgs = sample_conversation.user_messages
        assert len(user_msgs) == 2
        assert all(m.role == "user" for m in user_msgs)

    def test_turn_count(self, sample_conversation) -> None:
        """Test turn_count property."""
        assert sample_conversation.turn_count == 2


class TestChunk:
    """Tests for Chunk model."""

    def test_chunk_creation(self) -> None:
        """Test basic chunk creation."""
        chunk = Chunk(
            id="chunk-001",
            text="Some text content",
            source="conversation",
        )
        assert chunk.id == "chunk-001"
        assert chunk.text == "Some text content"
        assert chunk.source == "conversation"
        assert chunk.embedding is None
        assert chunk.metadata == {}

    def test_chunk_with_conversation_fields(self) -> None:
        """Test chunk with conversation-specific fields."""
        chunk = Chunk(
            id="conv-001-turn-0",
            text="Hello",
            source="conversation",
            conversation_id="conv-001",
            turn_index=0,
            total_turns=5,
        )
        assert chunk.conversation_id == "conv-001"
        assert chunk.turn_index == 0
        assert chunk.total_turns == 5


class TestWriting:
    """Tests for Writing model."""

    def test_writing_creation(self, sample_writing) -> None:
        """Test writing creation."""
        assert sample_writing.title == "On Durability"
        assert "durability" in sample_writing.content.lower()
        assert sample_writing.type == "essay"
        assert "philosophy" in sample_writing.tags


class TestEmail:
    """Tests for Email model."""

    def test_email_creation(self, sample_email) -> None:
        """Test email creation."""
        assert sample_email.from_addr == "alex@example.com"
        assert "friend@example.com" in sample_email.to
        assert "paper" in sample_email.subject.lower()


class TestBookmark:
    """Tests for Bookmark model."""

    def test_bookmark_creation(self, sample_bookmark) -> None:
        """Test bookmark creation."""
        assert "example.com" in sample_bookmark.url
        assert sample_bookmark.annotation is not None
        assert "category-theory" in sample_bookmark.tags


class TestPhoto:
    """Tests for Photo model."""

    def test_photo_creation(self, sample_photo) -> None:
        """Test photo creation."""
        assert sample_photo.path == "2024/01/mountains.jpg"
        assert sample_photo.caption is not None
        assert sample_photo.location == "Colorado"


class TestReading:
    """Tests for Reading model."""

    def test_reading_creation(self, sample_reading) -> None:
        """Test reading creation."""
        assert sample_reading.title == "Gödel, Escher, Bach"
        assert sample_reading.author == "Douglas Hofstadter"
        assert sample_reading.rating == 5
        assert len(sample_reading.highlights) == 1

    def test_highlight(self) -> None:
        """Test Highlight creation."""
        h = Highlight(text="Quote", note="My thoughts", location="p.42")
        assert h.text == "Quote"
        assert h.note == "My thoughts"
        assert h.location == "p.42"
