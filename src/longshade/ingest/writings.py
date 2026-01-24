"""Ingester for Markdown writing files with frontmatter."""

from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional, List

import frontmatter

from ..models import Writing
from .base import Ingester


class WritingIngester(Ingester[Writing]):
    """Ingest writings from Markdown files with YAML frontmatter.

    Expected format:
        ---
        title: Why I Care About Durability
        date: 2024-01-15
        tags: [philosophy, archiving]
        type: essay
        ---

        When I think about what matters...

    Frontmatter is optional but helpful for metadata.
    """

    def ingest(self, path: Path) -> Iterator[Writing]:
        """Ingest a writing from a Markdown file.

        Args:
            path: Path to Markdown file

        Yields:
            Single Writing object
        """
        with open(path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)

        # Parse date from frontmatter
        date: Optional[datetime] = None
        if "date" in post.metadata:
            date = self._parse_date(post.metadata["date"])

        # Parse tags
        tags: List[str] = []
        if "tags" in post.metadata:
            raw_tags = post.metadata["tags"]
            if isinstance(raw_tags, list):
                tags = [str(t) for t in raw_tags]
            elif isinstance(raw_tags, str):
                # Handle comma-separated tags
                tags = [t.strip() for t in raw_tags.split(",")]

        yield Writing(
            content=post.content,
            title=post.metadata.get("title"),
            date=date,
            tags=tags,
            type=post.metadata.get("type"),
            source_path=str(path),
        )

    def _parse_date(self, value: object) -> Optional[datetime]:
        """Parse date from frontmatter.

        Handles date objects, strings, and None.
        """
        if value is None:
            return None

        if isinstance(value, datetime):
            return value

        if hasattr(value, "isoformat"):  # date object
            # Convert date to datetime
            from datetime import date as date_type

            if isinstance(value, date_type):
                return datetime.combine(value, datetime.min.time())

        if isinstance(value, str):
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

        return None

    def ingest_directory(
        self, directory: Path, pattern: str = "*.md"
    ) -> Iterator[Writing]:
        """Ingest all Markdown files in a directory."""
        return super().ingest_directory(directory, pattern)
