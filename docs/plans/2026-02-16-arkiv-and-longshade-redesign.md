# Design: arkiv + longshade Redesign

**Date:** 2026-02-16
**Status:** Approved

---

## Summary

Split longshade into two projects:

1. **arkiv** -- Universal personal data format with JSONL canonical storage, SQLite query layer, and MCP server
2. **longshade** -- Thin persona packaging convention that uses arkiv

This eliminates the custom RAG implementation, the 7 specialized ingesters, and the approach-specific output formats. longshade becomes a simple tool that packages personal data as a conversable persona.

---

## Motivation

The current longshade implementation over-engineers retrieval (custom FAISS index, embedder, chunker) while under-investing in the foundational problem: getting personal data into a universal, durable, queryable format.

Key insights from design discussion:

- **JSONL is the universal interchange.** Independent sources (ctk, mtk, btk, ChatGPT exports, email dumps) each produce JSONL. You can `cat` them together. Human-readable, git-diffable, append-only.
- **Persona is memory.** More data = better simulacrum. The system should accept *everything* -- text, audio, images, video -- not just curated subsets.
- **RAG ages poorly.** FAISS indexes, embedding models, chunking strategies change every 6 months. Clean data + SQL + LLM intelligence is more durable.
- **MCP is the integration layer.** A generic SQLite MCP server (3 tools) replaces all the custom retrieval code. The LLM writes SQL to get what it needs.
- **The data format is independent of personas.** The universal record format is useful for archival, analytics, personal knowledge bases -- not just digital echoes.

---

## Project 1: arkiv

### What it is

A universal personal data format with tooling. JSONL is the canonical representation. SQLite is the query layer. MCP serves it to LLMs.

### Universal Record Format

Every record is a JSON object with all fields optional:

```jsonl
{"mimetype": "text/plain", "url": "https://chatgpt.com/c/abc123", "content": "I think the key insight is...", "timestamp": "2023-05-14T10:30:00Z", "metadata": {"conversation_id": "abc123", "role": "user"}}
{"mimetype": "text/markdown", "url": "https://myblog.com/on-durability", "content": "# Why I care about durability\n\nWhen I think about...", "timestamp": "2019-03-22", "metadata": {"title": "On Durability", "tags": ["philosophy"]}}
{"mimetype": "audio/wav", "url": "file://media/podcast-001.wav", "timestamp": "2024-01-15", "metadata": {"transcript": "Welcome to...", "duration": 45.2}}
{"mimetype": "image/jpeg", "url": "file://media/conference.jpg", "timestamp": "2024-01-15", "metadata": {"caption": "Giving my talk on category theory", "location": "MIT"}}
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `mimetype` | string | Standard MIME type (text/plain, audio/wav, image/jpeg, etc.) |
| `url` | string | URI reference (file://, http://, s3://, etc.) |
| `content` | string | Inline content (text for text types, base64 for binary) |
| `timestamp` | string | ISO 8601 datetime |
| `metadata` | object | Freeform JSON -- everything else |

**Design principles:**

- All fields optional. Any valid JSON object is a valid record.
- Permissive input, best-effort processing. Preserve everything, use what you can.
- `mimetype` describes the resource. `content` is the resource inlined. `url` is the resource by reference.
- One record = one resource = one mimetype.
- Derived representations (transcripts of audio, captions of images) go in `metadata`.
- Document-oriented, not relational. Records are self-contained with context baked in.

### manifest.json

Describes a collection of JSONL files:

```json
{
  "description": "Alex's personal data archive",
  "created": "2026-02-16",
  "metadata": {},
  "collections": [
    {
      "file": "conversations.jsonl",
      "description": "ChatGPT and Claude conversations 2022-2025",
      "record_count": 12847,
      "schema": {
        "metadata_keys": {
          "conversation_id": {"type": "string", "count": 12847, "example": "abc-123"},
          "role": {"type": "string", "count": 12847, "values": ["user", "assistant"]},
          "topic": {"type": "string", "count": 8432, "example": "category theory"},
          "source": {"type": "string", "count": 12847, "values": ["chatgpt", "claude"]}
        }
      }
    },
    {
      "file": "bookmarks.jsonl",
      "description": "Annotated bookmarks from btk",
      "record_count": 3200
    }
  ]
}
```

Schema is pre-computed at import time for efficient discovery.

### SQLite Schema

```sql
CREATE TABLE records (
    id INTEGER PRIMARY KEY,
    collection TEXT,        -- which JSONL file this came from
    mimetype TEXT,
    url TEXT,
    content TEXT,
    timestamp TEXT,
    metadata JSON
);

-- Pre-computed metadata schema for discovery
CREATE TABLE _schema (
    collection TEXT,
    key_path TEXT,          -- e.g. "role", "topic", "location"
    type TEXT,              -- string, number, boolean, array, object
    count INTEGER,
    sample_values TEXT      -- JSON array of example values
);

-- Useful indexes
CREATE INDEX idx_records_collection ON records(collection);
CREATE INDEX idx_records_mimetype ON records(mimetype);
CREATE INDEX idx_records_timestamp ON records(timestamp);
```

### MCP Server (3 tools)

| Tool | Description |
|------|-------------|
| `get_manifest()` | Returns manifest -- what collections exist, descriptions, pre-computed schemas |
| `get_schema(collection?)` | Returns metadata keys, types, value distributions. Optional collection filter. |
| `sql_query(query)` | Runs read-only SQL against the SQLite database |

The LLM calls `get_manifest()` to understand what's available, `get_schema()` to learn queryable metadata keys, then `sql_query()` to retrieve data.

### CLI

```bash
# Import JSONL to SQLite
arkiv import conversations.jsonl --db archive.db

# Import all collections via manifest
arkiv import manifest.json --db archive.db

# Export SQLite back to JSONL + manifest
arkiv export archive.db --output ./exported/

# Discover schema of a JSONL file
arkiv schema conversations.jsonl

# Query
arkiv query archive.db "SELECT content FROM records WHERE metadata->>'role' = 'user' LIMIT 5"

# Serve MCP
arkiv serve archive.db --port 8002
```

### Tech Stack

- Python 3.8+
- sqlite3 (stdlib)
- json (stdlib)
- MCP Python SDK for the server
- No heavy dependencies

---

## Project 2: longshade (Redesigned)

### What it is

A thin persona packaging convention on top of arkiv.

### What it does

1. Takes arkiv-format JSONL files (or a SQLite DB) as input
2. Generates a system prompt (personality distillation)
3. Extracts voice samples (curated few-shot Q&A pairs)
4. Copies/links media files (audio for voice cloning, images)
5. Packages it all as a persona directory

### Output

```
persona/
├── README.md              # Self-describing, always human-readable
├── manifest.json          # arkiv manifest with collection schemas
├── system-prompt.txt      # Distilled personality, works with any LLM
├── voice-samples.jsonl    # Curated few-shot Q&A examples
├── data.db                # SQLite (imported from JSONL, queryable via arkiv MCP)
├── media/                 # Audio clips, images, referenced by records
│   ├── podcast-001.wav
│   ├── conference.jpg
│   └── ...
└── corpus/                # Source JSONL files (canonical representation)
    ├── conversations.jsonl
    ├── writings.jsonl
    └── ...
```

### CLI

```bash
# Generate persona from arkiv-format input
longshade generate ./input/ --output ./persona/

# Inspect persona
longshade info ./persona/

# Serve (just delegates to arkiv serve)
longshade serve ./persona/
```

### What longshade does NOT do

- **No custom RAG.** No FAISS, no embeddings, no chunking. The LLM queries via arkiv's MCP server.
- **No specialized ingesters.** Source toolkits (ctk, mtk, btk) export arkiv-format JSONL. longshade accepts it as-is.
- **No approach-specific output.** No approaches/ directory. The persona is data + system prompt.
- **No retrieval logic.** The LLM writes SQL to get what it needs.

### What longshade DOES do

- **System prompt generation.** Analyze the data to distill personality, voice characteristics, values, interests, and boundaries into a system prompt.
- **Voice sample curation.** Extract representative Q&A pairs from conversations that demonstrate the persona's voice and tone.
- **Media organization.** Copy/link audio clips and images into the persona directory for voice cloning and visual reference.
- **Packaging.** Produce a self-describing, portable persona directory.

---

## Migration Path

### What gets removed from longshade

- `src/longshade/rag/` -- entire directory (chunker, embedder, index)
- `src/longshade/ingest/` -- 7 specialized ingesters replaced by arkiv import
- `src/longshade/output/persona.py` -- dramatically simplified (no approach-specific writers)
- `tests/test_chunker.py`, `tests/test_index.py`, `tests/test_ingest.py` -- replaced

### What gets created in arkiv

- Universal record format spec
- JSONL <-> SQLite import/export
- Schema discovery
- MCP server (3 tools)
- CLI

### What stays in longshade

- `src/longshade/config.py` -- simplified
- `src/longshade/cli.py` -- simplified (generate, info, serve)
- `src/longshade/models.py` -- simplified (just Voice for media handling?)
- System prompt generation (new)
- Voice sample curation (new)

---

## Architecture Diagram

```
Source Toolkits          arkiv                    longshade
┌─────────┐
│ ctk     │──┐
├─────────┤  │     ┌──────────────┐         ┌─────────────────┐
│ mtk     │──┼────→│ JSONL files  │────────→│ generate        │
├─────────┤  │     │ (universal   │         │  - system prompt │
│ btk     │──┤     │  records)    │         │  - voice samples │
├─────────┤  │     └──────┬───────┘         │  - package       │
│ ptk     │──┤            │                 └────────┬────────┘
├─────────┤  │     ┌──────▼───────┐                  │
│ ebk     │──┤     │ SQLite       │         ┌────────▼────────┐
├─────────┤  │     │ (query layer)│         │ persona/        │
│ ChatGPT │──┘     └──────┬───────┘         │  system-prompt  │
│ export  │               │                 │  data.db        │
└─────────┘        ┌──────▼───────┐         │  voice-samples  │
                   │ MCP server   │         │  media/         │
                   │  get_manifest│         │  manifest.json  │
                   │  get_schema  │         └─────────────────┘
                   │  sql_query   │
                   └──────────────┘
                         ▲
                         │
                   ┌─────┴──────┐
                   │ Any LLM    │
                   │ via MCP    │
                   └────────────┘
```

---

## ECHO Compliance

arkiv and ECHO are independent but compatible:

- **ECHO** is a philosophy: self-describing (README), durable formats, graceful degradation, local-first
- **arkiv** is a data format: JSONL + SQLite + manifest
- An arkiv archive with a README is automatically ECHO-compliant

Each source toolkit (ctk, btk, ebk, etc.) outputs an ECHO-compliant arkiv archive:

```
ctk-export/
├── README.md              # ECHO compliant (self-describing)
├── manifest.json          # arkiv manifest (schema discovery)
├── conversations.jsonl    # arkiv universal format (human-readable)
└── conversations.db       # arkiv SQLite (queryable)
```

Two degradation layers:
1. SQLite -- rich queries, JSON functions, indexing
2. JSONL -- cat, grep, text editors, git diff

The persona output directory is itself ECHO-compliant (has a README, uses durable formats).

---

## Open Questions

1. **Voice cloning data.** With the simplified design, should voice reference clips just live in media/ with metadata in the corpus? Or does longshade still organize them for convenience?

2. **System prompt generation.** This is the hardest remaining problem. How do we distill personality from raw data? Currently the system prompt is mostly static. Should this use an LLM to analyze the data and write the prompt?

3. **Infinigram integration.** The spec recommends infinigram for voice fidelity. With the simplified architecture, does infinigram just read from the same SQLite? Or does it need its own corpus format?

4. **Build order.** arkiv first (since longshade depends on it), then redesign longshade?
