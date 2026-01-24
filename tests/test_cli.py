"""Tests for CLI."""

import json
import pytest
from pathlib import Path

from longshade.cli import main


class TestCLI:
    """Tests for command-line interface."""

    def test_version(self, capsys) -> None:
        """Test --version flag."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "longshade" in captured.out

    def test_help(self, capsys) -> None:
        """Test no args shows help."""
        result = main([])
        assert result == 0

    def test_generate_missing_input(self, tmp_path: Path) -> None:
        """Test generate with missing input directory."""
        result = main(["generate", str(tmp_path / "nonexistent")])
        assert result == 1

    def test_analyze_counts_sources(
        self,
        tmp_input_dir: Path,
        conversations_jsonl: Path,
        writings_md: Path,
        capsys,
    ) -> None:
        """Test analyze command counts sources."""
        result = main(["analyze", str(tmp_input_dir)])

        assert result == 0
        captured = capsys.readouterr()
        assert "conversations:" in captured.out
        assert "writings:" in captured.out

    def test_info_missing_persona(self, tmp_path: Path) -> None:
        """Test info with missing persona directory."""
        result = main(["info", str(tmp_path / "nonexistent")])
        assert result == 1

    def test_info_invalid_persona(self, tmp_path: Path) -> None:
        """Test info with invalid persona (no manifest)."""
        persona_path = tmp_path / "persona"
        persona_path.mkdir()

        result = main(["info", str(persona_path)])
        assert result == 1

    def test_info_valid_persona(self, tmp_path: Path, capsys) -> None:
        """Test info with valid persona."""
        persona_path = tmp_path / "persona"
        persona_path.mkdir()

        manifest = {
            "version": "1.0",
            "name": "Test User",
            "generated": "2024-01-15T10:00:00",
            "sources": {"conversation": {"count": 10}},
            "approaches": {"rag": True, "infinigram": False},
        }
        (persona_path / "manifest.json").write_text(json.dumps(manifest))

        result = main(["info", str(persona_path)])

        assert result == 0
        captured = capsys.readouterr()
        assert "Test User" in captured.out
        assert "conversation:" in captured.out


class TestGenerateCommand:
    """Tests for generate command.

    Note: Full generate tests require sentence-transformers and faiss-cpu.
    """

    @pytest.mark.skipif(
        True,  # Skip by default - requires heavy dependencies
        reason="Requires sentence-transformers and faiss-cpu",
    )
    def test_generate_basic(
        self,
        tmp_input_dir: Path,
        conversations_jsonl: Path,
        writings_md: Path,
        tmp_path: Path,
    ) -> None:
        """Test basic generate command."""
        output_path = tmp_path / "output"

        # Create config
        config_content = """
persona:
  name: "Test Persona"
  description: "A test persona"
approaches:
  rag:
    enabled: true
  infinigram:
    enabled: false
  fine_tune:
    enabled: false
  tools:
    enabled: false
"""
        (tmp_input_dir / "longshade.yaml").write_text(config_content)

        result = main(
            [
                "generate",
                str(tmp_input_dir),
                "--output",
                str(output_path),
            ]
        )

        assert result == 0
        assert output_path.exists()
        assert (output_path / "manifest.json").exists()
        assert (output_path / "system-prompt.txt").exists()
        assert (output_path / "README.md").exists()
