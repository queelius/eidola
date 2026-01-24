"""Tests for data ingesters."""

import json
import pytest
from pathlib import Path

from longshade.ingest import (
    ConversationIngester,
    WritingIngester,
    EmailIngester,
    BookmarkIngester,
    PhotoIngester,
    ReadingIngester,
)


class TestConversationIngester:
    """Tests for ConversationIngester."""

    def test_ingest_conversations(self, conversations_jsonl: Path) -> None:
        """Test ingesting conversations from JSONL."""
        ingester = ConversationIngester()
        conversations = list(ingester.ingest(conversations_jsonl))

        assert len(conversations) == 1
        conv = conversations[0]
        assert conv.id == "conv-001"
        assert len(conv.messages) == 4

    def test_user_messages_extracted(self, conversations_jsonl: Path) -> None:
        """Test that user messages are correctly identified."""
        ingester = ConversationIngester()
        conversations = list(ingester.ingest(conversations_jsonl))

        conv = conversations[0]
        user_msgs = conv.user_messages
        assert len(user_msgs) == 2
        assert all(m.role == "user" for m in user_msgs)

    def test_conversation_title_inferred(self, conversations_jsonl: Path) -> None:
        """Test that title is inferred from first user message."""
        ingester = ConversationIngester()
        conversations = list(ingester.ingest(conversations_jsonl))

        conv = conversations[0]
        assert conv.title is not None
        assert "functional programming" in conv.title.lower()

    def test_missing_required_field(self, tmp_path: Path) -> None:
        """Test error on missing required field."""
        file_path = tmp_path / "bad.jsonl"
        file_path.write_text('{"role": "user"}\n')  # Missing content

        ingester = ConversationIngester()
        with pytest.raises(ValueError, match="Missing 'content'"):
            list(ingester.ingest(file_path))

    def test_ingest_directory(
        self, tmp_input_dir: Path, conversations_jsonl: Path
    ) -> None:
        """Test ingesting from directory."""
        ingester = ConversationIngester()
        conversations = list(ingester.ingest_directory(tmp_input_dir / "conversations"))
        assert len(conversations) == 1


class TestWritingIngester:
    """Tests for WritingIngester."""

    def test_ingest_writing(self, writings_md: Path) -> None:
        """Test ingesting writing from Markdown."""
        ingester = WritingIngester()
        writings = list(ingester.ingest(writings_md))

        assert len(writings) == 1
        writing = writings[0]
        assert writing.title == "On Durability"
        assert writing.type == "essay"
        assert "philosophy" in writing.tags
        assert "durability" in writing.content.lower()

    def test_writing_date_parsed(self, writings_md: Path) -> None:
        """Test that date is parsed from frontmatter."""
        ingester = WritingIngester()
        writings = list(ingester.ingest(writings_md))

        writing = writings[0]
        assert writing.date is not None
        assert writing.date.year == 2024
        assert writing.date.month == 1
        assert writing.date.day == 15

    def test_writing_without_frontmatter(self, tmp_path: Path) -> None:
        """Test writing without frontmatter."""
        file_path = tmp_path / "plain.md"
        file_path.write_text("Just some plain text without frontmatter.\n")

        ingester = WritingIngester()
        writings = list(ingester.ingest(file_path))

        assert len(writings) == 1
        assert writings[0].title is None
        assert "plain text" in writings[0].content


class TestEmailIngester:
    """Tests for EmailIngester."""

    def test_ingest_email(self, emails_jsonl: Path) -> None:
        """Test ingesting email from JSONL."""
        ingester = EmailIngester()
        emails = list(ingester.ingest(emails_jsonl))

        assert len(emails) == 1
        email = emails[0]
        assert email.from_addr == "alex@example.com"
        assert "friend@example.com" in email.to
        assert email.thread_id == "thread-123"

    def test_missing_from(self, tmp_path: Path) -> None:
        """Test error on missing from field."""
        file_path = tmp_path / "bad.jsonl"
        file_path.write_text('{"body": "Hello"}\n')

        ingester = EmailIngester()
        with pytest.raises(ValueError, match="Missing 'from'"):
            list(ingester.ingest(file_path))


class TestBookmarkIngester:
    """Tests for BookmarkIngester."""

    def test_ingest_bookmark(self, bookmarks_jsonl: Path) -> None:
        """Test ingesting bookmark from JSONL."""
        ingester = BookmarkIngester()
        bookmarks = list(ingester.ingest(bookmarks_jsonl))

        assert len(bookmarks) == 1
        bookmark = bookmarks[0]
        assert "example.com" in bookmark.url
        assert bookmark.annotation is not None
        assert "programming" in bookmark.tags

    def test_missing_url(self, tmp_path: Path) -> None:
        """Test error on missing url field."""
        file_path = tmp_path / "bad.jsonl"
        file_path.write_text('{"title": "No URL"}\n')

        ingester = BookmarkIngester()
        with pytest.raises(ValueError, match="Missing 'url'"):
            list(ingester.ingest(file_path))


class TestPhotoIngester:
    """Tests for PhotoIngester."""

    def test_ingest_photo(self, photos_jsonl: Path) -> None:
        """Test ingesting photo metadata from JSONL."""
        ingester = PhotoIngester()
        photos = list(ingester.ingest(photos_jsonl))

        assert len(photos) == 1
        photo = photos[0]
        assert photo.path == "2024/01/sunset.jpg"
        assert photo.caption is not None
        assert photo.location == "Colorado"

    def test_missing_path(self, tmp_path: Path) -> None:
        """Test error on missing path field."""
        file_path = tmp_path / "bad.jsonl"
        file_path.write_text('{"caption": "No path"}\n')

        ingester = PhotoIngester()
        with pytest.raises(ValueError, match="Missing 'path'"):
            list(ingester.ingest(file_path))


class TestReadingIngester:
    """Tests for ReadingIngester."""

    def test_ingest_reading(self, reading_jsonl: Path) -> None:
        """Test ingesting reading notes from JSONL."""
        ingester = ReadingIngester()
        readings = list(ingester.ingest(reading_jsonl))

        assert len(readings) == 1
        reading = readings[0]
        assert reading.title == "Gödel, Escher, Bach"
        assert reading.author == "Douglas Hofstadter"
        assert reading.rating == 5
        assert len(reading.highlights) == 1

    def test_reading_highlight(self, reading_jsonl: Path) -> None:
        """Test that highlights are parsed correctly."""
        ingester = ReadingIngester()
        readings = list(ingester.ingest(reading_jsonl))

        reading = readings[0]
        highlight = reading.highlights[0]
        assert "strange loop" in highlight.text
        assert highlight.note is not None
        assert highlight.location == "Ch 1"

    def test_missing_title(self, tmp_path: Path) -> None:
        """Test error on missing title field."""
        file_path = tmp_path / "bad.jsonl"
        file_path.write_text('{"author": "Someone"}\n')

        ingester = ReadingIngester()
        with pytest.raises(ValueError, match="Missing 'title'"):
            list(ingester.ingest(file_path))
