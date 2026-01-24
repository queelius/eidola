"""Shared test fixtures."""

import json
import pytest
from datetime import datetime
from pathlib import Path
from typing import List

from longshade.models import (
    Message,
    Conversation,
    Writing,
    Email,
    Bookmark,
    Photo,
    Reading,
    Highlight,
    Voice,
)


@pytest.fixture
def tmp_input_dir(tmp_path: Path) -> Path:
    """Create a temporary input directory with all subdirectories."""
    for subdir in [
        "conversations",
        "writings",
        "emails",
        "bookmarks",
        "photos",
        "reading",
        "voice",
    ]:
        (tmp_path / subdir).mkdir()
    return tmp_path


@pytest.fixture
def sample_messages() -> List[Message]:
    """Sample messages for testing."""
    return [
        Message(
            role="user",
            content="What do you think about functional programming?",
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            source="ctk",
            conversation_id="conv-001",
        ),
        Message(
            role="assistant",
            content="Functional programming emphasizes immutability...",
            timestamp=datetime(2024, 1, 15, 10, 31, 0),
            source="ctk",
            conversation_id="conv-001",
        ),
        Message(
            role="user",
            content="That makes sense. What about Haskell specifically?",
            timestamp=datetime(2024, 1, 15, 10, 32, 0),
            source="ctk",
            conversation_id="conv-001",
        ),
    ]


@pytest.fixture
def sample_conversation(sample_messages: List[Message]) -> Conversation:
    """Sample conversation for testing."""
    return Conversation(
        id="conv-001",
        messages=sample_messages,
        title="Discussion about functional programming",
        source="ctk",
        timestamp=datetime(2024, 1, 15, 10, 30, 0),
    )


@pytest.fixture
def sample_writing() -> Writing:
    """Sample writing for testing."""
    return Writing(
        content="""When I think about what matters in software, I keep coming back to durability.

Not just technical durability—though that matters—but conceptual durability. Will this idea still make sense in ten years? Will this abstraction still be useful?

The best code I've written isn't the cleverest. It's the simplest code that solved the problem clearly.""",
        title="On Durability",
        date=datetime(2024, 1, 15),
        tags=["philosophy", "software"],
        type="essay",
        source_path="essays/durability.md",
    )


@pytest.fixture
def sample_email() -> Email:
    """Sample email for testing."""
    return Email(
        from_addr="alex@example.com",
        body="I finally read the paper you sent. The key insight about category theory was fascinating...",
        to=["friend@example.com"],
        subject="Re: That paper you sent",
        timestamp=datetime(2024, 1, 15, 14, 30, 0),
        thread_id="thread-123",
    )


@pytest.fixture
def sample_bookmark() -> Bookmark:
    """Sample bookmark for testing."""
    return Bookmark(
        url="https://example.com/category-theory",
        title="Introduction to Category Theory",
        annotation="Great explanation of functors and natural transformations",
        tags=["math", "category-theory"],
        timestamp=datetime(2024, 1, 15, 9, 0, 0),
    )


@pytest.fixture
def sample_photo() -> Photo:
    """Sample photo for testing."""
    return Photo(
        path="2024/01/mountains.jpg",
        caption="That light over the mountains reminded me of home",
        location="Colorado",
        timestamp=datetime(2024, 1, 15, 18, 30, 0),
        tags=["nature", "sunset"],
        people=[],
    )


@pytest.fixture
def sample_reading() -> Reading:
    """Sample reading for testing."""
    return Reading(
        title="Gödel, Escher, Bach",
        author="Douglas Hofstadter",
        highlights=[
            Highlight(
                text="A strange loop arises when...",
                note="This connects to consciousness",
                location="Chapter 1",
            ),
        ],
        rating=5,
        review="Changed how I think about minds and self-reference",
        finished=datetime(2024, 1, 10),
        tags=["philosophy", "math", "ai"],
    )


@pytest.fixture
def conversations_jsonl(tmp_input_dir: Path) -> Path:
    """Create a sample conversations JSONL file."""
    file_path = tmp_input_dir / "conversations" / "sample.jsonl"
    messages = [
        {
            "role": "user",
            "content": "What do you think about functional programming?",
            "timestamp": "2024-01-15T10:30:00Z",
            "conversation_id": "conv-001",
            "source": "ctk",
        },
        {
            "role": "assistant",
            "content": "Functional programming emphasizes immutability and pure functions.",
            "timestamp": "2024-01-15T10:31:00Z",
            "conversation_id": "conv-001",
            "source": "ctk",
        },
        {
            "role": "user",
            "content": "That makes sense. What about Haskell specifically?",
            "timestamp": "2024-01-15T10:32:00Z",
            "conversation_id": "conv-001",
            "source": "ctk",
        },
        {
            "role": "assistant",
            "content": "Haskell is a purely functional language with strong typing.",
            "timestamp": "2024-01-15T10:33:00Z",
            "conversation_id": "conv-001",
            "source": "ctk",
        },
    ]
    with open(file_path, "w") as f:
        for msg in messages:
            f.write(json.dumps(msg) + "\n")
    return file_path


@pytest.fixture
def writings_md(tmp_input_dir: Path) -> Path:
    """Create a sample Markdown writing file."""
    file_path = tmp_input_dir / "writings" / "durability.md"
    content = """---
title: On Durability
date: 2024-01-15
tags: [philosophy, software]
type: essay
---

When I think about what matters in software, I keep coming back to durability.

Not just technical durability—though that matters—but conceptual durability.

The best code isn't the cleverest. It's the simplest code that solved the problem clearly.
"""
    file_path.write_text(content)
    return file_path


@pytest.fixture
def emails_jsonl(tmp_input_dir: Path) -> Path:
    """Create a sample emails JSONL file."""
    file_path = tmp_input_dir / "emails" / "sample.jsonl"
    emails = [
        {
            "from": "alex@example.com",
            "to": ["friend@example.com"],
            "subject": "Re: That paper",
            "body": "I finally read it. The key insight was fascinating.",
            "timestamp": "2024-01-15T14:30:00Z",
            "thread_id": "thread-123",
        },
    ]
    with open(file_path, "w") as f:
        for email in emails:
            f.write(json.dumps(email) + "\n")
    return file_path


@pytest.fixture
def bookmarks_jsonl(tmp_input_dir: Path) -> Path:
    """Create a sample bookmarks JSONL file."""
    file_path = tmp_input_dir / "bookmarks" / "sample.jsonl"
    bookmarks = [
        {
            "url": "https://example.com/article",
            "title": "Great Article",
            "annotation": "This explains the concept clearly",
            "tags": ["tech", "programming"],
            "timestamp": "2024-01-15T09:00:00Z",
        },
    ]
    with open(file_path, "w") as f:
        for bm in bookmarks:
            f.write(json.dumps(bm) + "\n")
    return file_path


@pytest.fixture
def photos_jsonl(tmp_input_dir: Path) -> Path:
    """Create a sample photos JSONL file."""
    file_path = tmp_input_dir / "photos" / "sample.jsonl"
    photos = [
        {
            "path": "2024/01/sunset.jpg",
            "caption": "Beautiful sunset over the mountains",
            "location": "Colorado",
            "timestamp": "2024-01-15T18:30:00Z",
            "tags": ["nature"],
        },
    ]
    with open(file_path, "w") as f:
        for photo in photos:
            f.write(json.dumps(photo) + "\n")
    return file_path


@pytest.fixture
def reading_jsonl(tmp_input_dir: Path) -> Path:
    """Create a sample reading JSONL file."""
    file_path = tmp_input_dir / "reading" / "sample.jsonl"
    readings = [
        {
            "title": "Gödel, Escher, Bach",
            "author": "Douglas Hofstadter",
            "highlights": [
                {
                    "text": "A strange loop...",
                    "note": "Connects to consciousness",
                    "location": "Ch 1",
                },
            ],
            "rating": 5,
            "review": "Changed how I think about minds",
            "finished": "2024-01-10",
            "tags": ["philosophy", "math"],
        },
    ]
    with open(file_path, "w") as f:
        for reading in readings:
            f.write(json.dumps(reading) + "\n")
    return file_path


@pytest.fixture
def sample_voice() -> Voice:
    """Sample voice recording for testing."""
    return Voice(
        path="clips/podcast-001.wav",
        transcript="I think the key insight is that simplicity matters.",
        duration=45.2,
        timestamp=datetime(2024, 1, 15, 10, 0, 0),
        context="podcast interview",
        language="en",
        speaker="Alex",
    )


@pytest.fixture
def voice_jsonl(tmp_input_dir: Path) -> Path:
    """Create a sample voice JSONL file."""
    file_path = tmp_input_dir / "voice" / "sample.jsonl"
    voices = [
        {
            "path": "clips/podcast-001.wav",
            "transcript": "I think the key insight is that simplicity matters.",
            "duration": 45.2,
            "timestamp": "2024-01-15T10:00:00Z",
            "context": "podcast interview",
            "language": "en",
        },
        {
            "path": "clips/voice-memo-001.wav",
            "caption": "Quick note about the project",
            "duration": 15.0,
            "timestamp": "2024-01-16T09:00:00Z",
        },
    ]
    with open(file_path, "w") as f:
        for voice in voices:
            f.write(json.dumps(voice) + "\n")
    return file_path
