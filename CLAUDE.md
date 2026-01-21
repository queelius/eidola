# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Status

**Specification-only.** No implementation exists yet. See SPEC.md for the full technical specification.

## What longshade Is

Generates a conversable persona from personal data:
- **Input**: Conversations, writings, emails, bookmarks, photos, reading notes (from toolkit ecosystem)
- **Output**: System prompt, RAG index, voice samples, infinigram corpus, MCP tools

Multiple approaches for persona instantiation:
1. **RAG** — Retrieval-augmented generation (portable baseline)
2. **Infinigram** — Probability mixing for authentic voice (recommended)
3. **Fine-tuning** — Model-specific training data
4. **Tool use** — MCP/function-calling for dynamic context

The goal: instantiate an LLM that speaks in your voice, with any provider.

## What longshade Is NOT

- **Not longecho** — longecho validates ECHO compliance; longshade creates personas
- **Not an LLM** — produces artifacts that work with any LLM
- **Not a chat interface** — that's planned but not the core purpose

## Key Principles

1. **Standalone toolkit** — Defines its own formats, works independently
2. **Privacy-conscious** — Personal data requires careful handling
3. **Portable output** — System prompt + RAG works with any LLM
4. **Voice fidelity** — Capture authentic voice, not hallucinate it

## Development Commands (When Implementation Begins)

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run single test
pytest tests/test_foo.py::test_bar -v

# Test coverage
pytest --cov=src/longshade --cov-report=term-missing

# Formatting
black src/ tests/

# Linting
flake8 src/ tests/

# Type checking
mypy src/
```

## Expected CLI Commands

```bash
# Core generation
longshade generate ./input/ --output ./persona/
longshade generate ./input/ --approaches rag,infinigram --output ./persona/
longshade analyze ./input/
longshade chat ./persona/
longshade evaluate ./persona/ --test-set ./test.jsonl

# Serving
longshade serve-infinigram ./persona/ --port 8001
longshade serve-mcp ./persona/ --port 8002

# Export and info
longshade export echo ./persona/ --output ./archive/
longshade info ./persona/
```

## Expected Tech Stack

- Python 3.8+, Typer (CLI), FAISS (vectors), sentence-transformers (embeddings)

## Related Projects

### Input Sources (Toolkit Ecosystem)

- [ctk](../ctk/) — Conversation export (strongest voice signal)
- [mtk](../mtk/) — Email/music toolkit (strong voice signal)
- [btk](../btk/) — Bookmark annotations (medium voice signal)
- [ptk](../ptk/) — Photo toolkit with captions (medium voice signal)
- [ebk](../ebk/) — Ebook toolkit with highlights/notes (medium voice signal)

### Persona Enhancement

- [infinigram](../infinigram/) — Suffix-array n-gram model for probability mixing (recommended enhancement)
- [langcalc](../langcalc/) — Algebraic language model composition (reference implementation)

### Compliance

- [longecho](../longecho/) — ECHO compliance validator
