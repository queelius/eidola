"""Data models for longshade."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import numpy as np


@dataclass
class Message:
    """A single message in a conversation.

    Required:
        role: "user" (your messages) or "assistant" (AI responses for context)
        content: Message text

    Optional:
        timestamp: ISO 8601 datetime
        source: Where this came from (for attribution)
        conversation_id: Group related messages
        topic: Subject/theme
    """

    role: str
    content: str
    timestamp: Optional[datetime] = None
    source: Optional[str] = None
    conversation_id: Optional[str] = None
    topic: Optional[str] = None

    def __post_init__(self) -> None:
        if self.role not in ("user", "assistant", "system"):
            raise ValueError(f"Invalid role: {self.role}")


@dataclass
class Conversation:
    """A group of related messages."""

    id: str
    messages: List[Message]
    title: Optional[str] = None
    source: Optional[str] = None
    timestamp: Optional[datetime] = None

    @property
    def user_messages(self) -> List[Message]:
        """Get only user messages (the persona's voice)."""
        return [m for m in self.messages if m.role == "user"]

    @property
    def turn_count(self) -> int:
        """Number of user turns."""
        return len(self.user_messages)


@dataclass
class Chunk:
    """A chunk for RAG indexing.

    For conversations, this is a single user turn with metadata
    for context expansion on retrieval.
    """

    id: str
    text: str
    source: str  # "conversation", "writing", "email", etc.
    embedding: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Conversation-specific fields for context expansion
    conversation_id: Optional[str] = None
    turn_index: Optional[int] = None
    total_turns: Optional[int] = None
    timestamp: Optional[datetime] = None


@dataclass
class Writing:
    """A long-form writing (essay, post, note, etc.).

    The body is Markdown content. Frontmatter is optional but helpful.
    """

    content: str
    title: Optional[str] = None
    date: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    type: Optional[str] = None  # essay, post, note, letter, etc.
    source_path: Optional[str] = None


@dataclass
class Email:
    """An email message.

    Only outgoing emails (where from matches persona) contribute to voice.
    """

    from_addr: str
    body: str
    to: List[str] = field(default_factory=list)
    cc: List[str] = field(default_factory=list)
    bcc: List[str] = field(default_factory=list)
    subject: Optional[str] = None
    timestamp: Optional[datetime] = None
    thread_id: Optional[str] = None
    in_reply_to: Optional[str] = None


@dataclass
class Bookmark:
    """A saved link with optional annotation.

    The annotation is the primary voice signal.
    """

    url: str
    title: Optional[str] = None
    annotation: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    timestamp: Optional[datetime] = None


@dataclass
class Photo:
    """Photo metadata with optional caption.

    The caption is the primary voice signal.
    """

    path: str
    caption: Optional[str] = None
    location: Optional[str] = None
    timestamp: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    people: List[str] = field(default_factory=list)


@dataclass
class Highlight:
    """A highlight from reading material."""

    text: str
    note: Optional[str] = None
    location: Optional[str] = None


@dataclass
class Reading:
    """Book, article, or other reading material.

    Reviews, notes, and highlight annotations are voice signals.
    """

    title: str
    author: Optional[str] = None
    highlights: List[Highlight] = field(default_factory=list)
    rating: Optional[int] = None
    review: Optional[str] = None
    finished: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class Voice:
    """Audio recording with optional transcript.

    Transcript is the primary voice signal for text RAG.
    Raw audio is used for voice cloning.

    Required:
        path: Audio file path (relative to voice/ directory)

    Optional:
        transcript: Full transcription (voice signal - strongest)
        caption: Brief description (voice signal - medium)
        duration: Length in seconds
        timestamp: When recorded
        context: Recording context (e.g., "podcast interview", "lecture")
        language: Language code (e.g., "en")
        speaker: Speaker identification (for multi-speaker audio)
    """

    path: str
    transcript: Optional[str] = None
    caption: Optional[str] = None
    duration: Optional[float] = None
    timestamp: Optional[datetime] = None
    context: Optional[str] = None
    language: Optional[str] = None
    speaker: Optional[str] = None
