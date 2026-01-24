"""Ingester for JSONL conversation files."""

import json
from datetime import datetime
from pathlib import Path
from typing import Iterator, List, Dict, Any, Optional

from ..models import Message, Conversation
from .base import Ingester


class ConversationIngester(Ingester[Conversation]):
    """Ingest conversations from JSONL files.

    Each line is a message with role and content.
    Messages are grouped into conversations by conversation_id.

    Expected format:
        {"role": "user", "content": "...", "timestamp": "...", "conversation_id": "..."}

    If conversation_id is not present, all messages in a file are
    treated as a single conversation.
    """

    def ingest(self, path: Path) -> Iterator[Conversation]:
        """Ingest conversations from a JSONL file.

        Args:
            path: Path to JSONL file

        Yields:
            Conversation objects
        """
        messages_by_conv: Dict[str, List[Message]] = {}
        default_conv_id = path.stem  # Use filename as default conversation ID

        with open(path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON at {path}:{line_num}: {e}") from e

                message = self._parse_message(data, line_num, path)
                conv_id = data.get("conversation_id", default_conv_id)
                message.conversation_id = conv_id

                if conv_id not in messages_by_conv:
                    messages_by_conv[conv_id] = []
                messages_by_conv[conv_id].append(message)

        # Yield conversations
        for conv_id, messages in messages_by_conv.items():
            # Sort by timestamp if available
            messages_with_ts = [m for m in messages if m.timestamp is not None]
            if len(messages_with_ts) == len(messages):
                messages.sort(key=lambda m: m.timestamp)  # type: ignore

            # Determine conversation timestamp from first message
            conv_timestamp = messages[0].timestamp if messages else None

            yield Conversation(
                id=conv_id,
                messages=messages,
                title=self._infer_title(messages),
                source=messages[0].source if messages else None,
                timestamp=conv_timestamp,
            )

    def _parse_message(
        self, data: Dict[str, Any], line_num: int, path: Path
    ) -> Message:
        """Parse a message from JSON data.

        Args:
            data: Parsed JSON object
            line_num: Line number for error reporting
            path: File path for error reporting

        Returns:
            Message object
        """
        # Required fields
        if "role" not in data:
            raise ValueError(f"Missing 'role' at {path}:{line_num}")
        if "content" not in data:
            raise ValueError(f"Missing 'content' at {path}:{line_num}")

        # Parse timestamp
        timestamp: Optional[datetime] = None
        if "timestamp" in data:
            timestamp = self._parse_timestamp(data["timestamp"])

        return Message(
            role=data["role"],
            content=data["content"],
            timestamp=timestamp,
            source=data.get("source"),
            conversation_id=data.get("conversation_id"),
            topic=data.get("topic"),
        )

    def _parse_timestamp(self, value: str) -> Optional[datetime]:
        """Parse ISO 8601 timestamp."""
        if not value:
            return None

        # Try common formats
        formats = [
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue

        # Try fromisoformat for Python 3.11+
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    def _infer_title(self, messages: List[Message]) -> Optional[str]:
        """Infer conversation title from first user message."""
        for msg in messages:
            if msg.role == "user" and msg.content:
                # Use first 50 chars of first user message
                title = msg.content[:50]
                if len(msg.content) > 50:
                    title += "..."
                return title
        return None

    def ingest_directory(
        self, directory: Path, pattern: str = "*.jsonl"
    ) -> Iterator[Conversation]:
        """Ingest all JSONL files in a directory."""
        return super().ingest_directory(directory, pattern)
