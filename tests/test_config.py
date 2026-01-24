"""Tests for configuration loading."""

import pytest
from pathlib import Path

from longshade.config import Config, load_config, save_config


class TestConfig:
    """Tests for Config dataclass."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = Config()
        assert config.persona_name == "Unknown"
        assert config.rag.enabled is True
        assert config.infinigram.enabled is True
        assert config.fine_tune.enabled is False

    def test_default_sources(self) -> None:
        """Test default source weights."""
        config = Config()
        assert config.sources["conversations"].weight == 1.0
        assert config.sources["writings"].weight == 0.9
        assert config.sources["bookmarks"].weight == 0.5

    def test_default_rag_config(self) -> None:
        """Test default RAG configuration."""
        config = Config()
        assert config.rag.chunk_size == 512
        assert config.rag.overlap == 64
        assert "all-MiniLM" in config.rag.embedding_model


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_nonexistent_returns_default(self, tmp_path: Path) -> None:
        """Test that loading nonexistent file returns default config."""
        config = load_config(tmp_path / "nonexistent.yaml")
        assert config.persona_name == "Unknown"

    def test_load_persona_config(self, tmp_path: Path) -> None:
        """Test loading persona configuration."""
        config_path = tmp_path / "longshade.yaml"
        config_path.write_text(
            """
persona:
  name: "Alex Towell"
  description: "Mathematician and software engineer"
"""
        )
        config = load_config(config_path)
        assert config.persona_name == "Alex Towell"
        assert "Mathematician" in config.persona_description

    def test_load_sources_config(self, tmp_path: Path) -> None:
        """Test loading sources configuration."""
        config_path = tmp_path / "longshade.yaml"
        config_path.write_text(
            """
sources:
  conversations:
    weight: 0.8
    filter: "^spam"
  writings:
    weight: 1.0
"""
        )
        config = load_config(config_path)
        assert config.sources["conversations"].weight == 0.8
        assert config.sources["conversations"].filter == "^spam"
        assert config.sources["writings"].weight == 1.0

    def test_load_approaches_config(self, tmp_path: Path) -> None:
        """Test loading approaches configuration."""
        config_path = tmp_path / "longshade.yaml"
        config_path.write_text(
            """
approaches:
  rag:
    enabled: true
    chunk_size: 256
  infinigram:
    enabled: false
    mixing_weight: 0.1
  fine_tune:
    enabled: true
    formats: ["openai"]
"""
        )
        config = load_config(config_path)
        assert config.rag.enabled is True
        assert config.rag.chunk_size == 256
        assert config.infinigram.enabled is False
        assert config.infinigram.mixing_weight == 0.1
        assert config.fine_tune.enabled is True

    def test_load_privacy_config(self, tmp_path: Path) -> None:
        """Test loading privacy configuration."""
        config_path = tmp_path / "longshade.yaml"
        # Use single quotes in YAML to avoid escape issues
        config_path.write_text(
            """
privacy:
  redact:
    - '\\d{3}-\\d{2}-\\d{4}'
  exclude_topics:
    - "medical"
    - "financial"
"""
        )
        config = load_config(config_path)
        assert len(config.privacy.redact) == 1
        assert "medical" in config.privacy.exclude_topics


class TestSaveConfig:
    """Tests for save_config function."""

    def test_save_and_reload(self, tmp_path: Path) -> None:
        """Test saving and reloading configuration."""
        original = Config()
        original.persona_name = "Test User"
        original.rag.chunk_size = 256

        config_path = tmp_path / "longshade.yaml"
        save_config(original, config_path)

        loaded = load_config(config_path)
        assert loaded.persona_name == "Test User"
        assert loaded.rag.chunk_size == 256

    def test_save_creates_parent_dirs(self, tmp_path: Path) -> None:
        """Test that save creates parent directories."""
        config = Config()
        config_path = tmp_path / "nested" / "dir" / "longshade.yaml"

        save_config(config, config_path)

        assert config_path.exists()
