"""Ingester for JSONL reading notes files."""

import json
from datetime import datetime
from pathlib import Path
from typing import Iterator, Dict, Any, Optional, List

from ..models import Reading, Highlight
from .base import Ingester


class ReadingIngester(Ingester[Reading]):
    """Ingest reading notes from JSONL files.

    Expected format:
        {"title": "Gödel, Escher, Bach", "author": "Douglas Hofstadter",
         "highlights": [{"text": "A strange loop...",
                        "note": "This connects to consciousness",
                        "location": "Chapter 1"}],
         "rating": 5, "review": "Changed how I think about minds",
         "finished": "2024-01-10", "tags": ["philosophy", "math"]}

    Required fields:
        - title: Book/article title

    Note: Reviews, notes, and highlight annotations are voice signals.
    Reading history shows intellectual interests.
    """

    def ingest(self, path: Path) -> Iterator[Reading]:
        """Ingest reading notes from a JSONL file.

        Args:
            path: Path to JSONL file

        Yields:
            Reading objects
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

                yield self._parse_reading(data, line_num, path)

    def _parse_reading(
        self, data: Dict[str, Any], line_num: int, path: Path
    ) -> Reading:
        """Parse a reading from JSON data."""
        # Required fields
        if "title" not in data:
            raise ValueError(f"Missing 'title' at {path}:{line_num}")

        # Parse finished date
        finished: Optional[datetime] = None
        if "finished" in data:
            finished = self._parse_date(data["finished"])

        # Parse highlights
        highlights: List[Highlight] = []
        if "highlights" in data:
            for h in data["highlights"]:
                if isinstance(h, dict) and "text" in h:
                    highlights.append(
                        Highlight(
                            text=h["text"],
                            note=h.get("note"),
                            location=h.get("location"),
                        )
                    )

        # Parse tags
        tags = self._parse_list(data.get("tags", []))

        # Parse rating
        rating: Optional[int] = None
        if "rating" in data:
            try:
                rating = int(data["rating"])
            except (ValueError, TypeError):
                pass

        return Reading(
            title=data["title"],
            author=data.get("author"),
            highlights=highlights,
            rating=rating,
            review=data.get("review"),
            finished=finished,
            tags=tags,
        )

    def _parse_list(self, value: object) -> List[str]:
        """Parse a list field."""
        if isinstance(value, list):
            return [str(v) for v in value]
        elif isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        return []

    def _parse_date(self, value: object) -> Optional[datetime]:
        """Parse date from various formats."""
        if value is None:
            return None

        if isinstance(value, datetime):
            return value

        if not isinstance(value, str):
            return None

        formats = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y/%m/%d",
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
    ) -> Iterator[Reading]:
        """Ingest all JSONL files in a directory."""
        return super().ingest_directory(directory, pattern)
