"""Ingester for JSONL email files."""

import json
from datetime import datetime
from pathlib import Path
from typing import Iterator, Dict, Any, Optional, List

from ..models import Email
from .base import Ingester


class EmailIngester(Ingester[Email]):
    """Ingest emails from JSONL files.

    Expected format:
        {"from": "alex@example.com", "to": ["friend@example.com"],
         "subject": "Re: That paper", "body": "I finally read it...",
         "timestamp": "2024-01-15T14:30:00Z", "thread_id": "thread-123"}

    Required fields:
        - from: Sender email
        - body: Email content

    Note: Only outgoing emails (where from matches persona) contribute
    to voice. Filter by persona email when processing.
    """

    def ingest(self, path: Path) -> Iterator[Email]:
        """Ingest emails from a JSONL file.

        Args:
            path: Path to JSONL file

        Yields:
            Email objects
        """
        with open(path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON at {path}:{line_num}: {e}") from e

                yield self._parse_email(data, line_num, path)

    def _parse_email(self, data: Dict[str, Any], line_num: int, path: Path) -> Email:
        """Parse an email from JSON data."""
        # Required fields
        if "from" not in data:
            raise ValueError(f"Missing 'from' at {path}:{line_num}")
        if "body" not in data:
            raise ValueError(f"Missing 'body' at {path}:{line_num}")

        # Parse timestamp
        timestamp: Optional[datetime] = None
        if "timestamp" in data:
            timestamp = self._parse_timestamp(data["timestamp"])

        # Parse recipient lists
        to = self._parse_recipients(data.get("to", []))
        cc = self._parse_recipients(data.get("cc", []))
        bcc = self._parse_recipients(data.get("bcc", []))

        return Email(
            from_addr=data["from"],
            body=data["body"],
            to=to,
            cc=cc,
            bcc=bcc,
            subject=data.get("subject"),
            timestamp=timestamp,
            thread_id=data.get("thread_id"),
            in_reply_to=data.get("in_reply_to"),
        )

    def _parse_recipients(self, value: object) -> List[str]:
        """Parse recipient list (can be string or list)."""
        if isinstance(value, list):
            return [str(v) for v in value]
        elif isinstance(value, str):
            return [value]
        return []

    def _parse_timestamp(self, value: str) -> Optional[datetime]:
        """Parse ISO 8601 timestamp."""
        if not value:
            return None

        formats = [
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%Y-%m-%d %H:%M:%S",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue

        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    def ingest_directory(
        self, directory: Path, pattern: str = "*.jsonl"
    ) -> Iterator[Email]:
        """Ingest all JSONL files in a directory."""
        return super().ingest_directory(directory, pattern)
