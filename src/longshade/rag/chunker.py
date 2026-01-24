"""Turn-level chunking for RAG indexing.

Key strategy from SPEC.md:
- Index each user turn as individual chunk
- Store conversation_id, turn_index, total_turns
- Context expansion on retrieval (±N turns)
"""

from dataclasses import dataclass
from typing import Iterator, List, Optional

from ..models import (
    Chunk, Conversation, Writing, Email, Bookmark, Photo, Reading, Voice
)


@dataclass
class ChunkerConfig:
    """Configuration for chunking."""

    # Context expansion settings
    context_turns: int = 3  # ±N turns for context
    max_context_turns: int = 10
    include_full_if_under: int = 20  # Full conversation if under N turns

    # Writing chunking
    chunk_size: int = 512  # Max chars per chunk for writings
    chunk_overlap: int = 64


class Chunker:
    """Chunker for creating RAG-indexable chunks from various sources."""

    def __init__(self, config: Optional[ChunkerConfig] = None):
        self.config = config or ChunkerConfig()

    def chunk_conversation(self, conversation: Conversation) -> Iterator[Chunk]:
        """Chunk a conversation into turn-level chunks.

        Each user turn becomes a chunk with metadata for context expansion.
        """
        user_turn_index = 0
        user_messages = conversation.user_messages

        for i, message in enumerate(conversation.messages):
            if message.role != "user":
                continue

            chunk_id = f"{conversation.id}-turn-{user_turn_index}"

            yield Chunk(
                id=chunk_id,
                text=message.content,
                source="conversation",
                embedding=None,
                metadata={
                    "message_index": i,  # Position in full message list
                    "source_type": conversation.source,
                    "title": conversation.title,
                },
                conversation_id=conversation.id,
                turn_index=user_turn_index,
                total_turns=len(user_messages),
                timestamp=message.timestamp,
            )
            user_turn_index += 1

    def chunk_writing(self, writing: Writing) -> Iterator[Chunk]:
        """Chunk a writing into paragraph or section-level chunks."""
        # Split on double newlines (paragraphs)
        paragraphs = [p.strip() for p in writing.content.split("\n\n") if p.strip()]

        # Combine small paragraphs, split large ones
        chunks: List[str] = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) < self.config.chunk_size:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                # Handle very long paragraphs
                if len(para) > self.config.chunk_size:
                    # Split by sentence or at max size
                    chunks.extend(self._split_long_text(para))
                else:
                    current_chunk = para

        if current_chunk:
            chunks.append(current_chunk)

        # Generate chunk objects
        source_id = writing.source_path or writing.title or "unknown"
        for i, chunk_text in enumerate(chunks):
            yield Chunk(
                id=f"writing-{source_id}-{i}",
                text=chunk_text,
                source="writing",
                embedding=None,
                metadata={
                    "title": writing.title,
                    "type": writing.type,
                    "tags": writing.tags,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                },
                timestamp=writing.date,
            )

    def chunk_email(self, email: Email) -> Iterator[Chunk]:
        """Chunk an email (usually single chunk unless very long)."""
        # Generate a stable ID from email attributes
        email_id = email.thread_id or hash(
            (email.from_addr, email.subject or "", email.body[:50])
        )

        text = email.body
        if email.subject:
            text = f"Subject: {email.subject}\n\n{email.body}"

        yield Chunk(
            id=f"email-{email_id}",
            text=text,
            source="email",
            embedding=None,
            metadata={
                "from": email.from_addr,
                "to": email.to,
                "subject": email.subject,
                "thread_id": email.thread_id,
            },
            timestamp=email.timestamp,
        )

    def chunk_bookmark(self, bookmark: Bookmark) -> Iterator[Chunk]:
        """Chunk a bookmark (single chunk, atomic).

        Only yields if annotation exists (the voice signal).
        """
        if not bookmark.annotation:
            return

        bookmark_id = hash(bookmark.url)

        yield Chunk(
            id=f"bookmark-{bookmark_id}",
            text=bookmark.annotation,
            source="bookmark",
            embedding=None,
            metadata={
                "url": bookmark.url,
                "title": bookmark.title,
                "tags": bookmark.tags,
            },
            timestamp=bookmark.timestamp,
        )

    def chunk_photo(self, photo: Photo) -> Iterator[Chunk]:
        """Chunk a photo (single chunk, atomic).

        Only yields if caption exists (the voice signal).
        """
        if not photo.caption:
            return

        yield Chunk(
            id=f"photo-{photo.path}",
            text=photo.caption,
            source="photo",
            embedding=None,
            metadata={
                "path": photo.path,
                "location": photo.location,
                "tags": photo.tags,
                "people": photo.people,
            },
            timestamp=photo.timestamp,
        )

    def chunk_reading(self, reading: Reading) -> Iterator[Chunk]:
        """Chunk reading material.

        Creates chunks for:
        - Review (if exists) - strong voice signal
        - Each highlight with note - voice signal
        """
        base_id = hash(reading.title + (reading.author or ""))

        # Review chunk
        if reading.review:
            yield Chunk(
                id=f"reading-review-{base_id}",
                text=reading.review,
                source="reading",
                embedding=None,
                metadata={
                    "title": reading.title,
                    "author": reading.author,
                    "rating": reading.rating,
                    "tags": reading.tags,
                    "chunk_type": "review",
                },
                timestamp=reading.finished,
            )

        # Highlight chunks (only those with notes)
        for i, highlight in enumerate(reading.highlights):
            if highlight.note:
                text = f"'{highlight.text}' - {highlight.note}"
                yield Chunk(
                    id=f"reading-highlight-{base_id}-{i}",
                    text=text,
                    source="reading",
                    embedding=None,
                    metadata={
                        "title": reading.title,
                        "author": reading.author,
                        "location": highlight.location,
                        "tags": reading.tags,
                        "chunk_type": "highlight",
                    },
                    timestamp=reading.finished,
                )

    def chunk_voice(self, voice: Voice) -> Iterator[Chunk]:
        """Chunk voice recordings by transcript/caption.

        Voice recordings yield a single chunk if they have text content
        (transcript or caption). Raw audio paths are preserved in metadata
        for voice cloning purposes.

        Only yields if transcript or caption exists (the voice signal).
        """
        text = voice.transcript or voice.caption
        if not text:
            return

        # Create a stable ID from the audio path
        chunk_id = f"voice-{voice.path}"

        yield Chunk(
            id=chunk_id,
            text=text,
            source="voice",
            embedding=None,
            metadata={
                "path": voice.path,
                "duration": voice.duration,
                "context": voice.context,
                "language": voice.language,
                "speaker": voice.speaker,
                "has_transcript": voice.transcript is not None,
            },
            timestamp=voice.timestamp,
        )

    def _split_long_text(self, text: str) -> List[str]:
        """Split long text into smaller chunks."""
        chunks = []
        max_size = self.config.chunk_size

        # Try to split on sentence boundaries
        sentences = text.replace(". ", ".|").split("|")
        current = ""

        for sentence in sentences:
            if len(current) + len(sentence) < max_size:
                current += sentence
            else:
                if current:
                    chunks.append(current.strip())
                if len(sentence) > max_size:
                    # Hard split if sentence is too long
                    for j in range(
                        0, len(sentence), max_size - self.config.chunk_overlap
                    ):
                        chunks.append(sentence[j : j + max_size])
                else:
                    current = sentence

        if current.strip():
            chunks.append(current.strip())

        return chunks


# Convenience functions
def chunk_conversations(
    conversations: List[Conversation], config: Optional[ChunkerConfig] = None
) -> List[Chunk]:
    """Chunk multiple conversations into turn-level chunks."""
    chunker = Chunker(config)
    chunks: List[Chunk] = []
    for conv in conversations:
        chunks.extend(chunker.chunk_conversation(conv))
    return chunks


def chunk_writings(
    writings: List[Writing], config: Optional[ChunkerConfig] = None
) -> List[Chunk]:
    """Chunk multiple writings into paragraph-level chunks."""
    chunker = Chunker(config)
    chunks: List[Chunk] = []
    for writing in writings:
        chunks.extend(chunker.chunk_writing(writing))
    return chunks


def chunk_voices(
    voices: List[Voice], config: Optional[ChunkerConfig] = None
) -> List[Chunk]:
    """Chunk multiple voice recordings into transcript/caption chunks."""
    chunker = Chunker(config)
    chunks: List[Chunk] = []
    for voice in voices:
        chunks.extend(chunker.chunk_voice(voice))
    return chunks
