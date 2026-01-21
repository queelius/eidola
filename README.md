# longshade: Conversable Persona Generation

**Status:** Specification Only — No Implementation Yet

---

## What is longshade?

longshade generates a **conversable persona** from personal data. Given conversations and writings, it produces everything needed to instantiate an LLM that can speak in your voice.

This is the "ghost" — your digital echo that can answer questions, share perspectives, and represent your thinking after you're gone.

*"The ghost is not you. But it echoes you."*

---

## Quick Start (Planned)

```bash
# Generate persona from input data
longshade generate ./input/ --output ./persona/

# Test the persona interactively
longshade chat ./persona/

# Analyze inputs without generating
longshade analyze ./input/
```

---

## Input Formats

### conversations/*.jsonl

Conversational data — your voice in dialogue.

```jsonl
{"role": "user", "content": "What do you think about...", "timestamp": "2024-01-15T10:30:00Z", "source": "ctk"}
{"role": "assistant", "content": "I think...", "timestamp": "2024-01-15T10:31:00Z", "source": "ctk"}
```

**Required fields:**
- `role`: "user" (your messages) or "assistant" (AI responses for context)
- `content`: Message text

**Optional fields:**
- `timestamp`: ISO 8601 datetime
- `source`: Where this came from (for attribution)
- `conversation_id`: Group related messages
- `topic`: Subject/theme

**Note:** Your messages (`role: "user"`) are the primary signal for voice. AI responses provide context but are not persona.

### writings/*.md

Long-form writing — your voice in prose.

```markdown
---
title: Why I Care About Durability
date: 2024-01-15
tags: [philosophy, archiving]
type: essay
---

When I think about what matters...
```

**Frontmatter (optional but helpful):**
- `title`: Title of the piece
- `date`: When written
- `tags`: Topics/themes
- `type`: essay, post, note, letter, etc.

---

## Output Format

longshade produces a `persona/` directory:

```
persona/
├── README.md           # How to use this persona
├── system-prompt.txt   # Ready-to-use LLM system prompt
├── rag/                # Embeddings and index for retrieval
│   ├── index.faiss
│   ├── metadata.json
│   └── chunks.jsonl
├── voice-samples.jsonl # Example Q&A pairs
└── fine-tune/          # Optional training data
```

The system prompt captures voice, values, and style. The RAG index enables grounded responses with semantic search. Voice samples demonstrate correct tone for few-shot prompting.

---

## How It Works

```
Any Source                        longshade                      Output
┌─────────────────┐              ┌─────────────────┐           ┌────────────────┐
│ conversations/  │─────────────→│                 │           │ persona/       │
│   *.jsonl       │              │ Analyze voice   │           │   README.md    │
├─────────────────┤              │ Extract style   │──────────→│   system-prompt│
│ writings/       │─────────────→│ Build RAG index │           │   rag/         │
│   *.md          │              │ Generate prompt │           │   voice-samples│
└─────────────────┘              └─────────────────┘           └────────────────┘
```

1. **Ingest** — Read conversations and writings
2. **Analyze** — Extract voice characteristics, values, patterns
3. **Chunk & Embed** — Build semantic search index
4. **Generate** — Produce system prompt and artifacts

---

## Standalone Toolkit

longshade is part of the ECHO ecosystem but works independently:

- **longshade defines what it accepts** — Input formats are longshade's specification
- **Any source can provide input** — If you can produce JSONL conversations or Markdown writings, longshade accepts them
- **Outputs are self-contained** — The persona directory works with any LLM

Compatible data sources:
- [ctk](https://github.com/aarontowell/ctk) — Conversation export
- [btk](https://github.com/aarontowell/btk) — Bookmark annotations
- Any tool that outputs JSONL or Markdown

---

## Privacy Considerations

longshade processes personal data. Consider:
- Review inputs before processing
- Think about what you're comfortable having in a conversable persona
- Use filtering options to exclude sensitive content
- Control who has access to the output

The generated persona can answer questions you never anticipated. Think carefully about what's included.

---

## Specification

For the complete technical specification, see [SPEC.md](SPEC.md).

---

## Related Projects

- [longecho](https://github.com/aarontowell/longecho) — ECHO compliance validator
- [ctk](https://github.com/aarontowell/ctk) — Conversation toolkit
- [btk](https://github.com/aarontowell/btk) — Bookmark toolkit
- [ebk](https://github.com/aarontowell/ebk) — Ebook toolkit

---

*"The ghost is not you. But it echoes you."*
