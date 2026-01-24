"""Configuration loading and management."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml


@dataclass
class SourceConfig:
    """Configuration for a single input source."""

    weight: float = 1.0
    filter: Optional[str] = None  # Regex to exclude patterns


@dataclass
class RAGConfig:
    """Configuration for RAG approach."""

    enabled: bool = True
    chunk_size: int = 512
    overlap: int = 64
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    context_turns: int = 3  # Number of turns for context expansion
    max_context_turns: int = 10
    include_full_if_under: int = 20  # Full conversation if under N turns


@dataclass
class InfinigramConfig:
    """Configuration for infinigram approach."""

    enabled: bool = True
    mixing_weight: float = 0.05
    adaptive: bool = True
    confidence_threshold: float = 0.7
    serve_port: int = 8001


@dataclass
class FineTuneConfig:
    """Configuration for fine-tuning approach."""

    enabled: bool = False
    formats: List[str] = field(default_factory=lambda: ["openai", "alpaca"])


@dataclass
class ToolsConfig:
    """Configuration for MCP/tools approach."""

    enabled: bool = True
    mcp_port: int = 8002


@dataclass
class VoiceConfig:
    """Configuration for voice/audio approach.

    Voice cloning stores reference audio and training data,
    not trained models. Supports multiple voice synthesis systems.
    """

    enabled: bool = True
    min_duration: float = 3.0  # Minimum clip duration for reference (seconds)
    max_reference_clips: int = 10  # Maximum clips to select for reference
    formats: List[str] = field(default_factory=lambda: ["chroma", "rvc", "xtts"])


@dataclass
class PrivacyConfig:
    """Privacy filtering configuration."""

    redact: List[str] = field(default_factory=list)  # Regex patterns
    exclude_topics: List[str] = field(default_factory=list)
    date_start: Optional[str] = None
    date_end: Optional[str] = None


@dataclass
class EchoConfig:
    """ECHO compliance configuration."""

    enabled: bool = True
    include_sources: bool = False


@dataclass
class Config:
    """Main longshade configuration.

    Matches the longshade.yaml schema from SPEC.md.
    """

    # Persona identity
    persona_name: str = "Unknown"
    persona_description: str = ""

    # Input source weighting
    sources: Dict[str, SourceConfig] = field(
        default_factory=lambda: {
            "conversations": SourceConfig(weight=1.0),
            "writings": SourceConfig(weight=0.9),
            "emails": SourceConfig(weight=0.8),
            "voice": SourceConfig(weight=0.6),
            "bookmarks": SourceConfig(weight=0.5),
            "photos": SourceConfig(weight=0.3),
            "reading": SourceConfig(weight=0.5),
        }
    )

    # Approach configurations
    rag: RAGConfig = field(default_factory=RAGConfig)
    infinigram: InfinigramConfig = field(default_factory=InfinigramConfig)
    fine_tune: FineTuneConfig = field(default_factory=FineTuneConfig)
    tools: ToolsConfig = field(default_factory=ToolsConfig)
    voice: VoiceConfig = field(default_factory=VoiceConfig)

    # Privacy and compliance
    privacy: PrivacyConfig = field(default_factory=PrivacyConfig)
    echo: EchoConfig = field(default_factory=EchoConfig)


def load_config(path: Path) -> Config:
    """Load configuration from a YAML file.

    Args:
        path: Path to longshade.yaml

    Returns:
        Config object with values from the file
    """
    if not path.exists():
        return Config()

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    config = Config()

    # Persona identity
    if "persona" in data:
        persona = data["persona"]
        config.persona_name = persona.get("name", config.persona_name)
        config.persona_description = persona.get(
            "description", config.persona_description
        )

    # Sources
    if "sources" in data:
        for source_name, source_data in data["sources"].items():
            if source_name in config.sources:
                config.sources[source_name] = SourceConfig(
                    weight=source_data.get("weight", 1.0),
                    filter=source_data.get("filter"),
                )

    # RAG approach
    if "approaches" in data and "rag" in data["approaches"]:
        rag = data["approaches"]["rag"]
        config.rag = RAGConfig(
            enabled=rag.get("enabled", True),
            chunk_size=rag.get("chunk_size", 512),
            overlap=rag.get("overlap", 64),
            embedding_model=rag.get("embedding_model", config.rag.embedding_model),
            context_turns=rag.get("context_turns", 3),
            max_context_turns=rag.get("max_context_turns", 10),
            include_full_if_under=rag.get("include_full_if_under", 20),
        )

    # Infinigram approach
    if "approaches" in data and "infinigram" in data["approaches"]:
        inf = data["approaches"]["infinigram"]
        config.infinigram = InfinigramConfig(
            enabled=inf.get("enabled", True),
            mixing_weight=inf.get("mixing_weight", 0.05),
            adaptive=inf.get("adaptive", True),
            confidence_threshold=inf.get("confidence_threshold", 0.7),
            serve_port=inf.get("serve_port", 8001),
        )

    # Fine-tune approach
    if "approaches" in data and "fine_tune" in data["approaches"]:
        ft = data["approaches"]["fine_tune"]
        config.fine_tune = FineTuneConfig(
            enabled=ft.get("enabled", False),
            formats=ft.get("formats", ["openai", "alpaca"]),
        )

    # Tools approach
    if "approaches" in data and "tools" in data["approaches"]:
        tools = data["approaches"]["tools"]
        config.tools = ToolsConfig(
            enabled=tools.get("enabled", True),
            mcp_port=tools.get("mcp_port", 8002),
        )

    # Voice approach
    if "approaches" in data and "voice" in data["approaches"]:
        voice = data["approaches"]["voice"]
        config.voice = VoiceConfig(
            enabled=voice.get("enabled", True),
            min_duration=voice.get("min_duration", 3.0),
            max_reference_clips=voice.get("max_reference_clips", 10),
            formats=voice.get("formats", ["chroma", "rvc", "xtts"]),
        )

    # Privacy
    if "privacy" in data:
        priv = data["privacy"]
        date_range = priv.get("date_range", {}) or {}
        config.privacy = PrivacyConfig(
            redact=priv.get("redact", []),
            exclude_topics=priv.get("exclude_topics", []),
            date_start=date_range.get("start"),
            date_end=date_range.get("end"),
        )

    # ECHO
    if "echo" in data:
        echo = data["echo"]
        config.echo = EchoConfig(
            enabled=echo.get("enabled", True),
            include_sources=echo.get("include_sources", False),
        )

    return config


def save_config(config: Config, path: Path) -> None:
    """Save configuration to a YAML file.

    Args:
        config: Config object to save
        path: Path to save to
    """
    data: Dict[str, Any] = {
        "persona": {
            "name": config.persona_name,
            "description": config.persona_description,
        },
        "sources": {
            name: {
                "weight": src.weight,
                "filter": src.filter,
            }
            for name, src in config.sources.items()
        },
        "approaches": {
            "rag": {
                "enabled": config.rag.enabled,
                "chunk_size": config.rag.chunk_size,
                "overlap": config.rag.overlap,
                "embedding_model": config.rag.embedding_model,
            },
            "infinigram": {
                "enabled": config.infinigram.enabled,
                "mixing_weight": config.infinigram.mixing_weight,
                "adaptive": config.infinigram.adaptive,
                "confidence_threshold": config.infinigram.confidence_threshold,
                "serve_port": config.infinigram.serve_port,
            },
            "fine_tune": {
                "enabled": config.fine_tune.enabled,
                "formats": config.fine_tune.formats,
            },
            "tools": {
                "enabled": config.tools.enabled,
                "mcp_port": config.tools.mcp_port,
            },
            "voice": {
                "enabled": config.voice.enabled,
                "min_duration": config.voice.min_duration,
                "max_reference_clips": config.voice.max_reference_clips,
                "formats": config.voice.formats,
            },
        },
        "privacy": {
            "redact": config.privacy.redact,
            "exclude_topics": config.privacy.exclude_topics,
            "date_range": {
                "start": config.privacy.date_start,
                "end": config.privacy.date_end,
            },
        },
        "echo": {
            "enabled": config.echo.enabled,
            "include_sources": config.echo.include_sources,
        },
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
