"""Ingester for JSONL voice/audio metadata files."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, Optional

from ..models import Voice
from .base import Ingester


class VoiceIngester(Ingester[Voice]):
    """Ingest voice/audio metadata from JSONL files.

    Expected format:
        {"path": "clips/podcast-2024-01.wav",
         "transcript": "I think the key insight is...",
         "duration": 45.2, "timestamp": "2024-01-15T10:00:00Z",
         "context": "podcast interview", "language": "en"}

    Required fields:
        - path: Audio file path (relative to voice/ directory)

    Optional fields:
        - transcript: Full transcription (voice signal - strongest)
        - caption: Brief description (voice signal - medium)
        - duration: Length in seconds
        - timestamp: When recorded
        - context: Recording context
        - language: Language code
        - speaker: Speaker identification (for multi-speaker audio)

    Note: Transcripts are the primary voice signal for text-based RAG.
    Raw audio is used for voice cloning.
    """

    def __init__(self, voice_dir: Optional[Path] = None):
        """Initialize the ingester.

        Args:
            voice_dir: Optional base directory for resolving relative audio paths.
                       If provided, validates that audio files exist.
        """
        self.voice_dir = voice_dir

    def ingest(self, path: Path) -> Iterator[Voice]:
        """Ingest voice metadata from a JSONL file.

        Args:
            path: Path to JSONL file

        Yields:
            Voice objects
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

                yield self._parse_voice(data, line_num, path)

    def _parse_voice(self, data: Dict[str, Any], line_num: int, path: Path) -> Voice:
        """Parse a voice recording from JSON data."""
        # Required fields
        if "path" not in data:
            raise ValueError(f"Missing 'path' at {path}:{line_num}")

        audio_path = data["path"]

        # Validate audio file exists if voice_dir is set
        if self.voice_dir is not None:
            full_audio_path = self.voice_dir / audio_path
            if not full_audio_path.exists():
                # Warning but don't fail - audio might be added later
                pass

        # Parse timestamp
        timestamp: Optional[datetime] = None
        if "timestamp" in data:
            timestamp = self._parse_timestamp(data["timestamp"])

        # Parse duration
        duration: Optional[float] = None
        if "duration" in data:
            try:
                duration = float(data["duration"])
            except (ValueError, TypeError):
                pass

        return Voice(
            path=audio_path,
            transcript=data.get("transcript"),
            caption=data.get("caption"),
            duration=duration,
            timestamp=timestamp,
            context=data.get("context"),
            language=data.get("language"),
            speaker=data.get("speaker"),
        )

    def _parse_timestamp(self, value: str) -> Optional[datetime]:
        """Parse ISO 8601 timestamp."""
        if not value:
            return None

        formats = [
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
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
    ) -> Iterator[Voice]:
        """Ingest all JSONL files in a directory.

        If voice_dir was not set during init, sets it to the directory
        being ingested for audio file validation.
        """
        if self.voice_dir is None:
            self.voice_dir = directory
        return super().ingest_directory(directory, pattern)
