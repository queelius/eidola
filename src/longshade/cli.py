"""Command-line interface for longshade."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from . import __version__
from .config import load_config
from .ingest import (
    ConversationIngester,
    WritingIngester,
    EmailIngester,
    BookmarkIngester,
    PhotoIngester,
    ReadingIngester,
    VoiceIngester,
)
from .models import Chunk, Conversation, Writing, Email, Bookmark, Photo, Reading, Voice
from .rag import Chunker, ChunkerConfig, Embedder, RAGIndex
from .output import PersonaWriter

console = Console()


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for longshade CLI."""
    parser = argparse.ArgumentParser(
        prog="longshade",
        description="Generate a conversable persona from personal data",
    )
    parser.add_argument(
        "--version", action="version", version=f"longshade {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # generate command
    gen_parser = subparsers.add_parser(
        "generate", help="Generate persona from input data"
    )
    gen_parser.add_argument("input", type=Path, help="Input directory")
    gen_parser.add_argument(
        "--output", "-o", type=Path, default=Path("./persona"), help="Output directory"
    )
    gen_parser.add_argument(
        "--config", "-c", type=Path, help="Path to longshade.yaml config file"
    )
    gen_parser.add_argument(
        "--approaches",
        type=str,
        help="Comma-separated list of approaches (rag,infinigram,fine-tune,tools)",
    )

    # analyze command
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze input data without generating"
    )
    analyze_parser.add_argument("input", type=Path, help="Input directory")
    analyze_parser.add_argument(
        "--config", "-c", type=Path, help="Path to longshade.yaml config file"
    )

    # info command
    info_parser = subparsers.add_parser("info", help="Show information about a persona")
    info_parser.add_argument("persona", type=Path, help="Persona directory")

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "generate":
        return cmd_generate(args)
    elif args.command == "analyze":
        return cmd_analyze(args)
    elif args.command == "info":
        return cmd_info(args)

    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    """Generate persona from input data."""
    input_path = args.input
    output_path = args.output

    if not input_path.is_dir():
        console.print(f"[red]Error: Input directory not found: {input_path}[/red]")
        return 1

    # Load config
    config_path = args.config or input_path / "longshade.yaml"
    config = load_config(config_path)

    console.print(f"[bold]Generating persona for {config.persona_name}[/bold]")
    console.print(f"Input: {input_path}")
    console.print(f"Output: {output_path}")
    console.print()

    # Ingest data
    conversations: List[Conversation] = []
    writings: List[Writing] = []
    emails: List[Email] = []
    bookmarks: List[Bookmark] = []
    photos: List[Photo] = []
    readings: List[Reading] = []
    voices: List[Voice] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Conversations
        conv_dir = input_path / "conversations"
        if conv_dir.is_dir():
            task = progress.add_task("Ingesting conversations...", total=None)
            conv_ingester = ConversationIngester()
            conversations = list(conv_ingester.ingest_directory(conv_dir, "*.jsonl"))
            progress.update(
                task, description=f"Ingested {len(conversations)} conversations"
            )

        # Writings
        writings_dir = input_path / "writings"
        if writings_dir.is_dir():
            task = progress.add_task("Ingesting writings...", total=None)
            writing_ingester = WritingIngester()
            writings = list(writing_ingester.ingest_directory(writings_dir, "*.md"))
            progress.update(task, description=f"Ingested {len(writings)} writings")

        # Emails
        emails_dir = input_path / "emails"
        if emails_dir.is_dir():
            task = progress.add_task("Ingesting emails...", total=None)
            email_ingester = EmailIngester()
            emails = list(email_ingester.ingest_directory(emails_dir, "*.jsonl"))
            progress.update(task, description=f"Ingested {len(emails)} emails")

        # Bookmarks
        bookmarks_dir = input_path / "bookmarks"
        if bookmarks_dir.is_dir():
            task = progress.add_task("Ingesting bookmarks...", total=None)
            bookmark_ingester = BookmarkIngester()
            bookmarks = list(
                bookmark_ingester.ingest_directory(bookmarks_dir, "*.jsonl")
            )
            progress.update(task, description=f"Ingested {len(bookmarks)} bookmarks")

        # Photos
        photos_dir = input_path / "photos"
        if photos_dir.is_dir():
            task = progress.add_task("Ingesting photos...", total=None)
            photo_ingester = PhotoIngester()
            photos = list(photo_ingester.ingest_directory(photos_dir, "*.jsonl"))
            progress.update(task, description=f"Ingested {len(photos)} photos")

        # Reading
        reading_dir = input_path / "reading"
        if reading_dir.is_dir():
            task = progress.add_task("Ingesting reading notes...", total=None)
            reading_ingester = ReadingIngester()
            readings = list(reading_ingester.ingest_directory(reading_dir, "*.jsonl"))
            progress.update(task, description=f"Ingested {len(readings)} reading notes")

        # Voice
        voice_dir = input_path / "voice"
        if voice_dir.is_dir():
            task = progress.add_task("Ingesting voice recordings...", total=None)
            voice_ingester = VoiceIngester(voice_dir)
            voices = list(voice_ingester.ingest_directory(voice_dir, "*.jsonl"))
            progress.update(task, description=f"Ingested {len(voices)} voice recordings")

    source_counts = {
        "conversation": len(conversations),
        "writing": len(writings),
        "email": len(emails),
        "bookmark": len(bookmarks),
        "photo": len(photos),
        "reading": len(readings),
        "voice": len(voices),
    }

    console.print()
    console.print("[bold]Source counts:[/bold]")
    for source, count in source_counts.items():
        if count > 0:
            console.print(f"  {source}: {count}")

    # Build RAG index if enabled
    rag_index = None
    if config.rag.enabled:
        console.print()
        console.print("[bold]Building RAG index...[/bold]")

        chunker_config = ChunkerConfig(
            context_turns=config.rag.context_turns,
            max_context_turns=config.rag.max_context_turns,
            include_full_if_under=config.rag.include_full_if_under,
            chunk_size=config.rag.chunk_size,
            chunk_overlap=config.rag.overlap,
        )
        chunker = Chunker(chunker_config)

        # Collect all chunks
        chunks: List[Chunk] = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Chunking data...", total=None)

            for conv in conversations:
                chunks.extend(chunker.chunk_conversation(conv))
            for writing in writings:
                chunks.extend(chunker.chunk_writing(writing))
            for email in emails:
                chunks.extend(chunker.chunk_email(email))
            for bookmark in bookmarks:
                chunks.extend(chunker.chunk_bookmark(bookmark))
            for photo in photos:
                chunks.extend(chunker.chunk_photo(photo))
            for reading in readings:
                chunks.extend(chunker.chunk_reading(reading))
            for voice in voices:
                chunks.extend(chunker.chunk_voice(voice))

            progress.update(task, description=f"Created {len(chunks)} chunks")

        if chunks:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Generating embeddings...", total=None)

                embedder = Embedder(config.rag.embedding_model)
                chunks = embedder.embed_chunks(chunks, show_progress=False)

                progress.update(task, description=f"Embedded {len(chunks)} chunks")

            # Build index
            rag_index = RAGIndex(embedder)
            rag_index.add_chunks(chunks)
            rag_index.add_conversations(conversations)

            console.print(f"  RAG index: {len(rag_index)} chunks")

    # Write persona
    console.print()
    console.print("[bold]Writing persona...[/bold]")

    writer = PersonaWriter(config, input_path=input_path)
    writer.write(output_path, rag_index, source_counts, voices=voices)

    console.print()
    console.print(f"[green]Persona written to {output_path}[/green]")

    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    """Analyze input data without generating."""
    input_path = args.input

    if not input_path.is_dir():
        console.print(f"[red]Error: Input directory not found: {input_path}[/red]")
        return 1

    console.print(f"[bold]Analyzing {input_path}[/bold]")
    console.print()

    # Count sources
    dirs = {
        "conversations": ("*.jsonl", ConversationIngester),
        "writings": ("*.md", WritingIngester),
        "emails": ("*.jsonl", EmailIngester),
        "bookmarks": ("*.jsonl", BookmarkIngester),
        "photos": ("*.jsonl", PhotoIngester),
        "reading": ("*.jsonl", ReadingIngester),
        "voice": ("*.jsonl", VoiceIngester),
    }

    for name, (pattern, ingester_cls) in dirs.items():
        dir_path = input_path / name
        if dir_path.is_dir():
            files = list(dir_path.glob(pattern))
            ingester = ingester_cls()
            items = list(ingester.ingest_directory(dir_path, pattern))  # type: ignore
            console.print(f"{name}: {len(items)} items from {len(files)} files")
        else:
            console.print(f"{name}: [dim]not found[/dim]")

    return 0


def cmd_info(args: argparse.Namespace) -> int:
    """Show information about a persona."""
    import json

    persona_path = args.persona

    if not persona_path.is_dir():
        console.print(f"[red]Error: Persona directory not found: {persona_path}[/red]")
        return 1

    manifest_path = persona_path / "manifest.json"
    if not manifest_path.exists():
        console.print("[red]Error: Not a valid persona (missing manifest.json)[/red]")
        return 1

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    console.print(f"[bold]{manifest.get('name', 'Unknown')}[/bold]")
    console.print(f"Generated: {manifest.get('generated', 'Unknown')}")
    console.print()

    console.print("[bold]Sources:[/bold]")
    for source, data in manifest.get("sources", {}).items():
        count = data.get("count", 0) if isinstance(data, dict) else data
        if count > 0:
            console.print(f"  {source}: {count}")

    console.print()
    console.print("[bold]Approaches:[/bold]")
    for approach, enabled in manifest.get("approaches", {}).items():
        status = "[green]enabled[/green]" if enabled else "[dim]disabled[/dim]"
        console.print(f"  {approach}: {status}")

    # Check RAG index
    rag_path = persona_path / "approaches" / "rag"
    if rag_path.is_dir():
        metadata_path = rag_path / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, "r", encoding="utf-8") as f:
                rag_metadata = json.load(f)
            console.print()
            console.print("[bold]RAG Index:[/bold]")
            console.print(f"  Chunks: {rag_metadata.get('total_chunks', 'Unknown')}")
            console.print(f"  Model: {rag_metadata.get('embedding_model', 'Unknown')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
