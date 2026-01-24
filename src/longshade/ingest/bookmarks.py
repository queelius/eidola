"""Ingester for JSONL bookmark files."""

import json
from datetime import datetime
from pathlib import Path
from typing import Iterator, Dict, Any, Optional, List

from ..models import Bookmark
from .base import Ingester


class BookmarkIngester(Ingester[Bookmark]):
    """Ingest bookmarks from JSONL files.

    Expected format:
        {"url": "https://example.com/article", "title": "Interesting Article",
         "annotation": "Great explanation of category theory",
         "tags": ["math", "category-theory"], "timestamp": "2024-01-15T09:00:00Z"}

    Required fields:
        - url: Bookmarked URL

    Note: The annotation is the primary voice signal. URLs and titles
    provide topic/interest data.
    """

    def ingest(self, path: Path) -> Iterator[Bookmark]:
        """Ingest bookmarks from a JSONL file.

        Args:
            path: Path to JSONL file

        Yields:
            Bookmark objects
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

                yield self._parse_bookmark(data, line_num, path)

    def _parse_bookmark(
        self, data: Dict[str, Any], line_num: int, path: Path
    ) -> Bookmark:
        """Parse a bookmark from JSON data."""
        # Required fields
        if "url" not in data:
            raise ValueError(f"Missing 'url' at {path}:{line_num}")

        # Parse timestamp
        timestamp: Optional[datetime] = None
        if "timestamp" in data:
            timestamp = self._parse_timestamp(data["timestamp"])

        # Parse tags
        tags = self._parse_tags(data.get("tags", []))

        return Bookmark(
            url=data["url"],
            title=data.get("title"),
            annotation=data.get("annotation"),
            tags=tags,
            timestamp=timestamp,
        )

    def _parse_tags(self, value: object) -> List[str]:
        """Parse tags (can be list or comma-separated string)."""
        if isinstance(value, list):
            return [str(t) for t in value]
        elif isinstance(value, str):
            return [t.strip() for t in value.split(",") if t.strip()]
        return []

    def _parse_timestamp(self, value: str) -> Optional[datetime]:
        """Parse ISO 8601 timestamp."""
        if not value:
            return None

        formats = [
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%fZ",
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
    ) -> Iterator[Bookmark]:
        """Ingest all JSONL files in a directory."""
        return super().ingest_directory(directory, pattern)
