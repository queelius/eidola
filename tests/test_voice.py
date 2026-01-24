"""Tests for voice/audio support."""

import json
import pytest
from datetime import datetime
from pathlib import Path

from longshade.ingest import VoiceIngester
from longshade.models import Voice
from longshade.rag.chunker import Chunker


class TestVoiceModel:
    """Tests for Voice dataclass."""

    def test_voice_creation(self) -> None:
        """Test creating a Voice object."""
        voice = Voice(
            path="clips/test.wav",
            transcript="Hello world",
            duration=10.5,
        )
        assert voice.path == "clips/test.wav"
        assert voice.transcript == "Hello world"
        assert voice.duration == 10.5

    def test_voice_minimal(self) -> None:
        """Test Voice with only required field."""
        voice = Voice(path="test.wav")
        assert voice.path == "test.wav"
        assert voice.transcript is None
        assert voice.caption is None
        assert voice.duration is None

    def test_voice_all_fields(self) -> None:
        """Test Voice with all fields."""
        voice = Voice(
            path="clips/podcast.wav",
            transcript="I think the key insight is...",
            caption="Podcast discussion",
            duration=45.2,
            timestamp=datetime(2024, 1, 15, 10, 0, 0),
            context="podcast interview",
            language="en",
            speaker="Alex",
        )
        assert voice.path == "clips/podcast.wav"
        assert voice.transcript == "I think the key insight is..."
        assert voice.caption == "Podcast discussion"
        assert voice.duration == 45.2
        assert voice.timestamp == datetime(2024, 1, 15, 10, 0, 0)
        assert voice.context == "podcast interview"
        assert voice.language == "en"
        assert voice.speaker == "Alex"


class TestVoiceIngester:
    """Tests for VoiceIngester."""

    def test_ingest_voice(self, voice_jsonl: Path) -> None:
        """Test ingesting voice from JSONL."""
        ingester = VoiceIngester()
        voices = list(ingester.ingest(voice_jsonl))

        assert len(voices) == 2
        voice = voices[0]
        assert voice.path == "clips/podcast-001.wav"
        assert voice.transcript == "I think the key insight is that simplicity matters."
        assert voice.duration == 45.2
        assert voice.context == "podcast interview"

    def test_ingest_voice_with_caption(self, voice_jsonl: Path) -> None:
        """Test ingesting voice with caption instead of transcript."""
        ingester = VoiceIngester()
        voices = list(ingester.ingest(voice_jsonl))

        # Second voice has caption, no transcript
        voice = voices[1]
        assert voice.path == "clips/voice-memo-001.wav"
        assert voice.transcript is None
        assert voice.caption == "Quick note about the project"
        assert voice.duration == 15.0

    def test_missing_path(self, tmp_path: Path) -> None:
        """Test error on missing path field."""
        file_path = tmp_path / "bad.jsonl"
        file_path.write_text('{"transcript": "No path"}\n')

        ingester = VoiceIngester()
        with pytest.raises(ValueError, match="Missing 'path'"):
            list(ingester.ingest(file_path))

    def test_ingest_directory(
        self, tmp_input_dir: Path, voice_jsonl: Path
    ) -> None:
        """Test ingesting from directory."""
        ingester = VoiceIngester()
        voices = list(ingester.ingest_directory(tmp_input_dir / "voice"))
        assert len(voices) == 2

    def test_timestamp_parsing(self, tmp_path: Path) -> None:
        """Test various timestamp formats."""
        file_path = tmp_path / "timestamps.jsonl"
        records = [
            {"path": "a.wav", "timestamp": "2024-01-15T10:00:00Z"},
            {"path": "b.wav", "timestamp": "2024-01-15"},
            {"path": "c.wav", "timestamp": "2024-01-15 10:30:00"},
        ]
        with open(file_path, "w") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")

        ingester = VoiceIngester()
        voices = list(ingester.ingest(file_path))

        assert len(voices) == 3
        assert voices[0].timestamp is not None
        assert voices[1].timestamp is not None
        assert voices[2].timestamp is not None


class TestVoiceChunking:
    """Tests for voice chunking."""

    def test_chunk_voice_with_transcript(self, sample_voice: Voice) -> None:
        """Test chunking voice with transcript."""
        chunker = Chunker()
        chunks = list(chunker.chunk_voice(sample_voice))

        assert len(chunks) == 1
        chunk = chunks[0]
        assert chunk.source == "voice"
        assert chunk.text == sample_voice.transcript
        assert chunk.metadata["path"] == sample_voice.path
        assert chunk.metadata["has_transcript"] is True

    def test_chunk_voice_with_caption(self) -> None:
        """Test chunking voice with caption instead of transcript."""
        voice = Voice(
            path="memo.wav",
            caption="Quick note about the project",
            duration=15.0,
        )
        chunker = Chunker()
        chunks = list(chunker.chunk_voice(voice))

        assert len(chunks) == 1
        chunk = chunks[0]
        assert chunk.text == "Quick note about the project"
        assert chunk.metadata["has_transcript"] is False

    def test_chunk_voice_no_text(self) -> None:
        """Test chunking voice without transcript or caption yields nothing."""
        voice = Voice(path="silent.wav", duration=60.0)
        chunker = Chunker()
        chunks = list(chunker.chunk_voice(voice))

        assert len(chunks) == 0

    def test_chunk_voice_metadata(self) -> None:
        """Test that voice metadata is preserved in chunk."""
        voice = Voice(
            path="clips/lecture.wav",
            transcript="Category theory is about composition.",
            duration=120.5,
            context="university lecture",
            language="en",
            speaker="Alex",
        )
        chunker = Chunker()
        chunks = list(chunker.chunk_voice(voice))

        chunk = chunks[0]
        assert chunk.metadata["duration"] == 120.5
        assert chunk.metadata["context"] == "university lecture"
        assert chunk.metadata["language"] == "en"
        assert chunk.metadata["speaker"] == "Alex"

    def test_chunk_voice_id(self) -> None:
        """Test that chunk ID is based on path."""
        voice = Voice(path="clips/test.wav", transcript="Hello")
        chunker = Chunker()
        chunks = list(chunker.chunk_voice(voice))

        assert chunks[0].id == "voice-clips/test.wav"


class TestVoiceConfig:
    """Tests for VoiceConfig."""

    def test_default_voice_config(self) -> None:
        """Test default VoiceConfig values."""
        from longshade.config import VoiceConfig

        config = VoiceConfig()
        assert config.enabled is True
        assert config.min_duration == 3.0
        assert config.max_reference_clips == 10
        assert "chroma" in config.formats
        assert "rvc" in config.formats
        assert "xtts" in config.formats

    def test_voice_in_default_sources(self) -> None:
        """Test that voice is in default sources."""
        from longshade.config import Config

        config = Config()
        assert "voice" in config.sources
        assert config.sources["voice"].weight == 0.6
