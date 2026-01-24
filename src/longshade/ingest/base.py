"""Base ingester interface."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator, TypeVar, Generic

T = TypeVar("T")


class Ingester(ABC, Generic[T]):
    """Abstract base class for data ingesters.

    Each ingester reads a specific format and yields typed objects.
    """

    @abstractmethod
    def ingest(self, path: Path) -> Iterator[T]:
        """Ingest data from a path.

        Args:
            path: Path to a file or directory

        Yields:
            Typed objects for each record
        """
        pass

    def ingest_directory(self, directory: Path, pattern: str = "*") -> Iterator[T]:
        """Ingest all matching files in a directory.

        Args:
            directory: Directory to scan
            pattern: Glob pattern for files (e.g., "*.jsonl")

        Yields:
            Typed objects from all matching files
        """
        if not directory.is_dir():
            raise ValueError(f"Not a directory: {directory}")

        for file_path in sorted(directory.glob(pattern)):
            if file_path.is_file():
                yield from self.ingest(file_path)
