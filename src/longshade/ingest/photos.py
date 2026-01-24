"""Ingester for JSONL photo metadata files."""

import json
from datetime import datetime
from pathlib import Path
from typing import Iterator, Dict, Any, Optional, List

from ..models import Photo
from .base import Ingester


class PhotoIngester(Ingester[Photo]):
    """Ingest photo metadata from JSONL files.

    Expected format:
        {"path": "2024/01/sunset.jpg", "caption": "That light over the mountains...",
         "location": "Colorado", "timestamp": "2024-01-15T18:30:00Z",
         "tags": ["nature", "sunset"], "people": ["Alice", "Bob"]}

    Required fields:
        - path: Photo file path (relative to source)

    Note: The caption is the primary voice signal. Photo metadata provides
    life context.
    """

    def ingest(self, path: Path) -> Iterator[Photo]:
        """Ingest photo metadata from a JSONL file.

        Args:
            path: Path to JSONL file

        Yields:
            Photo objects
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

                yield self._parse_photo(data, line_num, path)

    def _parse_photo(self, data: Dict[str, Any], line_num: int, path: Path) -> Photo:
        """Parse a photo from JSON data."""
        # Required fields
        if "path" not in data:
            raise ValueError(f"Missing 'path' at {path}:{line_num}")

        # Parse timestamp
        timestamp: Optional[datetime] = None
        if "timestamp" in data:
            timestamp = self._parse_timestamp(data["timestamp"])

        # Parse lists
        tags = self._parse_list(data.get("tags", []))
        people = self._parse_list(data.get("people", []))

        return Photo(
            path=data["path"],
            caption=data.get("caption"),
            location=data.get("location"),
            timestamp=timestamp,
            tags=tags,
            people=people,
        )

    def _parse_list(self, value: object) -> List[str]:
        """Parse a list field (can be list or comma-separated string)."""
        if isinstance(value, list):
            return [str(v) for v in value]
        elif isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
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
            "%Y:%m:%d %H:%M:%S",  # EXIF format
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
    ) -> Iterator[Photo]:
        """Ingest all JSONL files in a directory."""
        return super().ingest_directory(directory, pattern)
