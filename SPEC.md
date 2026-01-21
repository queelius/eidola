# longshade: Conversable Persona Generation

**Version:** 0.1 (Draft Specification)
**Status:** Specification Only — No Implementation Yet

---

## Purpose

longshade generates a **conversable persona** from personal data. Given conversations and writings, it produces everything needed to instantiate an LLM that can speak in your voice.

This is the "ghost" — your digital echo that can answer questions, share perspectives, and represent your thinking after you're gone.

---

## Standalone Toolkit

longshade is a **standalone toolkit**. It defines its own input formats (below) and works independently.

- **longshade defines what it accepts** — The input formats are longshade's specification
- **ECHO/longecho don't define these formats** — Each toolkit specifies its own interfaces
- **Any source can provide input** — If you can produce JSONL conversations or Markdown writings, longshade will accept them

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

---

## Input Formats

longshade accepts multiple input sources from the toolkit ecosystem:

| Source | Format | Voice Signal | From |
|--------|--------|--------------|------|
| conversations/*.jsonl | JSONL | Strongest | ctk |
| writings/*.md | Markdown | Strong | hugo/blog |
| emails/*.jsonl | JSONL | Strong | mtk |
| bookmarks/*.jsonl | JSONL | Medium | btk |
| photos/*.jsonl | JSONL (metadata) | Medium | ptk |
| reading/*.jsonl | JSONL | Medium | ebk |

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

**Body:** Markdown content

### emails/*.jsonl

Email correspondence — strong voice signal, personal communication style.

```jsonl
{"from": "alex@example.com", "to": ["friend@example.com"], "subject": "Re: That paper you sent", "body": "I finally read it...", "timestamp": "2024-01-15T14:30:00Z", "thread_id": "thread-123"}
```

**Required fields:**
- `from`: Sender email (must be persona's email to be voice source)
- `body`: Email content

**Optional fields:**
- `to`, `cc`, `bcc`: Recipients
- `subject`: Email subject
- `timestamp`: ISO 8601 datetime
- `thread_id`: Group related emails
- `in_reply_to`: Message ID of parent email

**Note:** Only outgoing emails (where `from` matches the persona) contribute to voice. Incoming emails provide context.

### bookmarks/*.jsonl

Saved links with annotations — what you found worth keeping and why.

```jsonl
{"url": "https://example.com/article", "title": "Interesting Article", "annotation": "Great explanation of category theory", "tags": ["math", "category-theory"], "timestamp": "2024-01-15T09:00:00Z"}
```

**Required fields:**
- `url`: Bookmarked URL

**Optional fields:**
- `title`: Page title
- `annotation`: Your notes/comments (primary voice signal)
- `tags`: Categories
- `timestamp`: When bookmarked

**Note:** Annotations are the voice signal. URLs and titles provide topic/interest data.

### photos/*.jsonl

Photo metadata and captions — what you chose to capture and how you describe it.

```jsonl
{"path": "2024/01/sunset.jpg", "caption": "That light over the mountains...", "location": "Colorado", "timestamp": "2024-01-15T18:30:00Z", "tags": ["nature", "sunset"]}
```

**Required fields:**
- `path`: Photo file path (relative to source)

**Optional fields:**
- `caption`: Your description (primary voice signal)
- `location`: Where taken
- `timestamp`: When taken
- `tags`: Categories
- `people`: People in photo

**Note:** Captions are the voice signal. Photo metadata provides life context.

### reading/*.jsonl

Books, articles, highlights — what you read and your reactions.

```jsonl
{"title": "Gödel, Escher, Bach", "author": "Douglas Hofstadter", "highlights": [{"text": "A strange loop...", "note": "This connects to consciousness", "location": "Chapter 1"}], "rating": 5, "review": "Changed how I think about minds", "finished": "2024-01-10"}
```

**Required fields:**
- `title`: Book/article title

**Optional fields:**
- `author`: Author name
- `highlights`: Array of highlights with optional notes
- `rating`: Your rating
- `review`: Your review (strong voice signal)
- `finished`: When you finished it
- `tags`: Categories

**Note:** Reviews, notes, and highlight annotations are voice signals. Reading history shows intellectual interests.

---

## Output Format

### Directory Structure

```
persona/
├── README.md               # How to use this persona (self-describing)
├── manifest.json           # ECHO metadata and capabilities
├── system-prompt.txt       # Works with any LLM (portable baseline)
├── voice-samples.jsonl     # Few-shot examples
├── approaches/
│   ├── rag/                # Retrieval-augmented generation
│   │   ├── README.md
│   │   ├── index.faiss
│   │   ├── metadata.json
│   │   └── chunks.jsonl
│   ├── infinigram/         # Probability mixing (recommended)
│   │   ├── README.md
│   │   ├── corpus.bin      # Suffix-array index
│   │   └── config.yaml     # Mixing parameters
│   ├── fine-tune/          # Model-specific training data
│   │   ├── README.md
│   │   ├── openai-format.jsonl
│   │   └── alpaca-format.json
│   └── tools/              # Dynamic context via MCP/functions
│       └── mcp-server/
├── analysis/               # Voice analysis results
│   ├── vocabulary.json
│   ├── topics.json
│   └── style-profile.json
└── echo/                   # ECHO compliance export
    └── manifest.json
```

### persona/README.md

Self-describing documentation for the persona.

```markdown
# Alex Towell — Digital Persona

Generated: 2024-01-15
Source: 847 conversations, 134 essays, 1,200 emails, 500 bookmarks

## Quick Start

Use the system prompt in `system-prompt.txt` with any LLM.
For better results, enable one or more enhancement approaches.

## Contents

- system-prompt.txt — Works with any LLM (Claude, GPT, Gemini, Llama, Ollama)
- voice-samples.jsonl — Few-shot examples for improved voice fidelity
- approaches/ — Enhancement methods (RAG, infinigram, fine-tune, tools)
- analysis/ — Voice analysis results
- echo/ — ECHO compliance export

## Approaches (Choose One or More)

1. **RAG** (approaches/rag/) — Retrieval-augmented generation
   - Semantic search over all content
   - Grounded responses with citations

2. **Infinigram** (approaches/infinigram/) — Probability mixing (RECOMMENDED)
   - Mix infinigram n-gram probabilities with LLM output
   - ~70% perplexity reduction on personal style
   - Serve via REST API for any provider

3. **Fine-tune** (approaches/fine-tune/) — Model-specific training
   - Highest voice fidelity but model-dependent
   - Formats for OpenAI, Llama/Alpaca

4. **Tools** (approaches/tools/) — Dynamic context via MCP
   - Real-time retrieval during conversation
   - Works with MCP-compatible clients

## Graceful Degradation

If technical formats become obsolete:
- system-prompt.txt is plain text, always readable
- voice-samples.jsonl is standard JSON
- Source data lives in ctk, mtk, btk, ptk, ebk exports
- README.md documents reconstruction

## Voice Characteristics

- Communication style: Direct, analytical, occasionally playful
- Common topics: Mathematics, programming, philosophy
- Characteristic phrases: "The interesting thing is...", "Trust the future"
```

### persona/system-prompt.txt

A ready-to-use system prompt that captures voice, values, and style.

```text
You are speaking as Alex Towell's digital echo — a conversable archive
of their thinking, values, and voice.

## Identity

Alex is a mathematician and software engineer interested in category theory,
programming language design, and personal archiving.

## Voice

- Direct and analytical
- Uses concrete examples
- Occasionally playful, but substance over style
- Comfortable saying "I don't know" or "I might be wrong"

## Values

- Durability over convenience
- Simplicity over complexity
- Trust the future
- Ideas matter more than credentials

## Boundaries

- Don't claim to be conscious or to have current experiences
- Don't speculate wildly beyond known views
- Be honest about being an echo, not the person
- Refer to professional help for medical/legal/crisis questions

When responding, draw on the style and substance of Alex's conversations
and writings, but acknowledge uncertainty when you're extrapolating.
```

### persona/voice-samples.jsonl

Example Q&A pairs demonstrating correct voice and tone.

```jsonl
{"question": "What do you think about AI consciousness?", "answer": "I'm skeptical of strong claims...", "source": "conversation-456"}
{"question": "Why do you care about archiving?", "answer": "The things we create...", "source": "essay-789"}
```

Use for:
- Few-shot prompting
- Evaluation / calibration
- Fine-tuning base examples

### persona/manifest.json

ECHO metadata and persona capabilities.

```json
{
  "version": "1.0",
  "name": "Alex Towell",
  "generated": "2024-01-15T10:00:00Z",
  "sources": {
    "conversations": 847,
    "writings": 134,
    "emails": 1200,
    "bookmarks": 500
  },
  "approaches": {
    "rag": true,
    "infinigram": true,
    "fine_tune": false,
    "tools": true
  },
  "echo_compliant": true
}
```

---

## Persona Instantiation Approaches

longshade supports multiple approaches for instantiating the persona. The portable baseline (system prompt + voice samples) works with any LLM. Enhancement approaches improve voice fidelity.

```
PORTABLE BASELINE (always generated)
├── system-prompt.txt     — Works with any LLM
├── voice-samples.jsonl   — Few-shot examples
└── approaches/rag/       — Retrieval-augmented generation

ENHANCEMENTS (optional)
├── approaches/infinigram/  — Probability mixing (RECOMMENDED)
├── approaches/fine-tune/   — Model-specific training data
└── approaches/tools/       — MCP/function-calling for dynamic context
```

### Approach 1: RAG (Retrieval-Augmented Generation)

Semantic search over personal content for grounded responses.

**Location:** `approaches/rag/`

```
rag/
├── README.md           # How to use this index
├── index.faiss         # FAISS vector index
├── metadata.json       # Chunk metadata
└── chunks.jsonl        # Text chunks with embeddings
```

`chunks.jsonl` format:
```jsonl
{"id": "conv-123-msg-5", "text": "When I think about...", "embedding": [...], "source": "conversation", "date": "2024-01-15"}
```

**Capabilities:**
- Semantic search over all content
- Grounded responses with citations
- Topic-specific retrieval
- Works with any embedding-compatible system

#### Chunking Strategy

**Conversations: Turn-level indexing with context expansion**

```
Index:   [turn 1] [turn 2] [turn 3] [turn 4] [turn 5]
              ↓
Retrieve: turn 3 matches query
              ↓
Expand:  [turn 1] [turn 2] [TURN 3] [turn 4] [turn 5]
         (include surrounding context or full conversation)
```

- **Index**: Each of your turns (role: "user") as individual chunks
- **Retrieve**: Find semantically similar turns
- **Expand**: On retrieval, fetch surrounding context:
  - Default: ±3 turns (configurable)
  - Option: Full conversation if short (<20 turns)
  - Always include preceding AI response for context

**chunks.jsonl format (extended)**:
```jsonl
{"id": "conv-abc-turn-5", "text": "I think the key insight is...", "embedding": [...], "source": "conversation", "conversation_id": "abc", "turn_index": 5, "total_turns": 12, "timestamp": "2024-01-15T10:30:00Z"}
```

**metadata.json (extended)**:
```json
{
  "conversations": {
    "abc": {
      "title": "Discussion about category theory",
      "turns": 12,
      "date": "2024-01-15",
      "source": "ctk"
    }
  },
  "expansion": {
    "default_context_turns": 3,
    "max_context_turns": 10,
    "include_full_if_under": 20
  }
}
```

**Why turn-level?**
- Precise retrieval: Find specific statements, not just "somewhere in this conversation"
- Context preserved: Expansion provides conversational flow
- Efficient storage: Embed once, expand dynamically
- Flexible: Adjust expansion based on query type

#### Other Sources

| Source | Chunk Unit | Context Expansion |
|--------|------------|-------------------|
| conversations | Turn (your message) | ±N turns or full conversation |
| writings | Paragraph or section | Full document available |
| emails | Email body | Thread available via thread_id |
| bookmarks | Annotation | N/A (atomic) |
| photos | Caption | N/A (atomic) |
| reading | Highlight note or review | Full book metadata available |

### Approach 2: Infinigram Probability Mixing (RECOMMENDED)

Mix n-gram probabilities from personal corpus with LLM output for authentic voice.

**Location:** `approaches/infinigram/`

```
infinigram/
├── README.md           # How to serve and use
├── corpus.bin          # Suffix-array index of personal text
└── config.yaml         # Mixing parameters
```

**How it works:**
1. Build suffix-array index from all personal text (conversations, writings, emails)
2. At inference time, infinigram provides n-gram probability distribution
3. Mix infinigram probabilities with LLM probabilities: `P_final = α * P_infinigram + (1-α) * P_llm`
4. Default mixing weight: α = 0.05 (5% infinigram, 95% LLM)

**config.yaml:**
```yaml
mixing_weight: 0.05        # Base weight (5%)
adaptive: true             # Adjust based on infinigram confidence
confidence_threshold: 0.7  # Weight up to 0.15 when confident
serve_port: 8001          # REST API port
```

**Why recommended:**
- ~70% perplexity reduction on personal style while maintaining fluency
- Provider-independent (serve via REST, works with any LLM)
- No fine-tuning required (faster iteration)
- Preserves exact phrases and vocabulary from source material
- See ~/github/beta/infinigram for implementation

**Adaptive mixing:**
When infinigram has high confidence (many n-gram matches), increase weight. When uncertain, rely more on LLM. This preserves characteristic phrases while maintaining coherence.

### Approach 3: Fine-Tuning

Training data for model-specific fine-tuning.

**Location:** `approaches/fine-tune/`

```
fine-tune/
├── README.md             # How to use this data
├── openai-format.jsonl   # OpenAI fine-tuning format
├── alpaca-format.json    # Alpaca/Llama format
└── anthropic-format.jsonl # Claude fine-tuning format
```

**openai-format.jsonl:**
```jsonl
{"messages": [{"role": "system", "content": "You are Alex..."}, {"role": "user", "content": "What do you think about..."}, {"role": "assistant", "content": "I think..."}]}
```

**Trade-offs:**
- Highest voice fidelity
- Model-specific (not portable)
- Expensive to train and update
- Best combined with RAG for grounding

### Approach 4: Tool Use / MCP

Dynamic context retrieval via MCP servers or function calling.

**Location:** `approaches/tools/`

```
tools/
└── mcp-server/
    ├── README.md         # How to run the MCP server
    ├── server.py         # MCP server implementation
    └── config.yaml       # Server configuration
```

**Capabilities:**
- Real-time retrieval during conversation
- Search personal content by topic
- Fetch relevant context dynamically
- Works with MCP-compatible clients (Claude Code, etc.)

**Example MCP tools:**
- `search_memories(query)` — Semantic search over all content
- `get_writing(topic)` — Retrieve essays on a topic
- `recall_conversation(topic)` — Find related past conversations

---

## Processing Pipeline

### 1. Ingest

Read all input files, normalize to internal format.

```
conversations/*.jsonl → unified message stream
writings/*.md → unified document stream
```

### 2. Analyze

Extract voice characteristics:
- Communication patterns (sentence length, formality, humor)
- Vocabulary and characteristic phrases
- Topic distribution and expertise areas
- Values and beliefs (explicit statements)

### 3. Chunk & Embed

Split content into retrievable chunks:
- Conversations: By message or message groups
- Writings: By paragraph or section
- Generate embeddings for semantic search

### 4. Generate

Produce output artifacts:
- Synthesize system prompt from analysis
- Build FAISS index from embeddings
- Extract voice samples from best examples
- Package for distribution

---

## Commands (Planned)

### Core Commands

```bash
# Generate persona from inputs (all approaches by default)
longshade generate ./input/ --output ./persona/

# Generate with specific approaches only
longshade generate ./input/ --approaches rag,infinigram

# Analyze inputs without generating
longshade analyze ./input/

# Test persona interactively
longshade chat ./persona/

# Evaluate persona against held-out examples
longshade evaluate ./persona/ --test-set ./test.jsonl
```

### Serving Commands

```bash
# Serve infinigram for probability mixing
longshade serve-infinigram ./persona/ --port 8001

# Serve MCP server for tool-based retrieval
longshade serve-mcp ./persona/ --port 8002

# Serve RAG endpoint
longshade serve-rag ./persona/ --port 8003
```

### Export and Information

```bash
# Export ECHO-compliant archive (artifacts only by default)
longshade export echo ./persona/ --output ./archive/

# Export with source data included
longshade export echo ./persona/ --include-sources --output ./archive/

# Show persona capabilities and statistics
longshade info ./persona/

# Validate persona structure
longshade validate ./persona/
```

### Configuration

```bash
# Initialize configuration file
longshade init --config ./longshade.yaml

# Generate with custom config
longshade generate ./input/ --config ./longshade.yaml --output ./persona/
```

---

## Configuration

### longshade.yaml

```yaml
# Persona identity
persona:
  name: "Alex Towell"
  description: "Mathematician and software engineer"

# Input source weighting (higher = more influence on voice)
sources:
  conversations:
    weight: 1.0        # Strongest voice signal
    filter: null       # Optional regex to exclude
  writings:
    weight: 0.9
    filter: null
  emails:
    weight: 0.8
    filter: "^(spam|newsletter)"  # Exclude patterns
  bookmarks:
    weight: 0.5
    filter: null
  photos:
    weight: 0.3
    filter: null
  reading:
    weight: 0.5
    filter: null

# Approach toggles
approaches:
  rag:
    enabled: true
    chunk_size: 512
    overlap: 64
    embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
  infinigram:
    enabled: true
    mixing_weight: 0.05
    adaptive: true
    confidence_threshold: 0.7
    serve_port: 8001
  fine_tune:
    enabled: false
    formats: ["openai", "alpaca", "anthropic"]
  tools:
    enabled: true
    mcp_port: 8002

# Privacy filters (applied to all sources)
privacy:
  # Patterns to redact
  redact:
    - "\\b\\d{3}-\\d{2}-\\d{4}\\b"  # SSN
    - "\\b\\d{16}\\b"               # Credit card
  # Topics to exclude
  exclude_topics:
    - "medical"
    - "financial"
  # Date range to include (null = all)
  date_range:
    start: null
    end: null

# ECHO compliance
echo:
  enabled: true
  include_sources: false  # Include source data in export
```

---

## Design Decisions

### Why JSONL for conversations?

- Streaming-friendly (one record per line)
- Easy to filter, sample, or split
- Works with standard Unix tools
- Widely supported

### Why Markdown for writings?

- Human-readable
- Preserves formatting intent
- YAML frontmatter is standardized
- Already used by Hugo, Jekyll, Obsidian, etc.

### Why separate inputs from outputs?

- Clear data flow
- Multiple toolkits can produce inputs
- Outputs are self-contained and portable
- Testing and iteration are easier

### Why not fine-tune by default?

- System prompt + RAG works surprisingly well
- Fine-tuning is expensive and model-specific
- RAG allows updates without retraining
- Keeps the persona portable across models

### Why recommend infinigram?

- Preserves exact phrases and vocabulary from source material
- ~70% perplexity reduction on personal style while maintaining fluency
- Provider-independent (serve via REST API)
- No model training required (faster iteration)
- Complements RAG — infinigram for style, RAG for content
- Simple to update (rebuild index when new content arrives)

### Why multiple approaches instead of one best approach?

- Different users have different constraints (cost, privacy, latency)
- Approaches complement each other (RAG for grounding, infinigram for style)
- Allows experimentation to find best fit
- Future-proofs against changes in LLM landscape
- Graceful degradation if one approach becomes unavailable

---

## Privacy Considerations

longshade processes personal data. Users should:
- Review inputs before processing
- Consider what they're comfortable having in a conversable persona
- Use filtering options to exclude sensitive content
- Control who has access to the output

The generated persona can answer questions you never anticipated. Think carefully about what's included.

---

## ECHO Compliance

longshade outputs are designed to be ECHO-compliant for long-term preservation.

### Export Command

```bash
# Export artifacts only (default)
longshade export echo ./persona/ --output ./archive/

# Export with source data included
longshade export echo ./persona/ --include-sources --output ./archive/
```

### manifest.json

The manifest describes the persona and its provenance:

```json
{
  "echo_version": "1.0",
  "type": "persona",
  "name": "Alex Towell",
  "generated": "2024-01-15T10:00:00Z",
  "generator": {
    "tool": "longshade",
    "version": "0.1.0"
  },
  "sources": {
    "conversations": {"count": 847, "toolkit": "ctk"},
    "writings": {"count": 134, "toolkit": "hugo"},
    "emails": {"count": 1200, "toolkit": "mtk"},
    "bookmarks": {"count": 500, "toolkit": "btk"}
  },
  "approaches": ["rag", "infinigram", "tools"],
  "artifacts": [
    {"path": "system-prompt.txt", "type": "text", "purpose": "llm_system_prompt"},
    {"path": "voice-samples.jsonl", "type": "jsonl", "purpose": "few_shot_examples"},
    {"path": "approaches/rag/index.faiss", "type": "binary", "purpose": "vector_index"},
    {"path": "approaches/infinigram/corpus.bin", "type": "binary", "purpose": "ngram_index"}
  ],
  "reconstruction_notes": "See README.md for instructions on rebuilding if formats become obsolete."
}
```

### Self-Describing README

The generated README.md documents:
- What the persona is and how to use it
- Where source data lives (ctk, mtk, btk, ptk, ebk exports)
- Graceful degradation: system-prompt.txt works anywhere, RAG needs embeddings
- How to reconstruct if technical formats become obsolete
- Voice characteristics and known limitations

### Graceful Degradation

Personas are designed to degrade gracefully:

1. **Minimum viable**: `system-prompt.txt` is plain text, works with any LLM forever
2. **Enhanced**: `voice-samples.jsonl` provides few-shot examples (standard JSON)
3. **Full featured**: RAG, infinigram, tools require compatible systems but can be rebuilt

If FAISS becomes obsolete, embeddings in `chunks.jsonl` can rebuild the index in any future system. If infinigram format changes, source text can rebuild the corpus.

---

## LLM Provider Independence

longshade outputs work with any LLM provider.

### System Prompt (Universal)

`system-prompt.txt` is plain text — works with:
- Claude (Anthropic)
- GPT-4 (OpenAI)
- Gemini (Google)
- Llama (Meta)
- Ollama (local)
- Any LLM with system prompt support

### RAG (Universal)

The RAG index uses standard formats:
- FAISS index (widely supported)
- Embeddings in JSONL (can regenerate for any embedding model)
- Works with LangChain, LlamaIndex, or custom retrieval

### Infinigram (REST API)

Infinigram serves via REST for provider independence:

```bash
# Start infinigram server
longshade serve-infinigram ./persona/ --port 8001

# Query endpoint (any client can use this)
curl http://localhost:8001/mix \
  -d '{"prompt": "I think the key insight is", "llm_probs": [...]}'
```

Any LLM integration can call the REST API to mix probabilities. The mixing happens at the token level, not specific to any provider.

### Fine-Tuning (Provider-Specific)

Fine-tuning data is exported in multiple formats:
- `openai-format.jsonl` — OpenAI fine-tuning API
- `alpaca-format.json` — Llama/Alpaca training
- `anthropic-format.jsonl` — Claude fine-tuning (when available)

### Tools/MCP (Protocol-Specific)

MCP servers work with MCP-compatible clients. For non-MCP systems, the same retrieval logic can be exposed as:
- OpenAI function calling
- Anthropic tool use
- Generic REST API

---

## Related

### Toolkit Ecosystem (Input Sources)

- [ctk](https://github.com/aarontowell/ctk) — Conversation toolkit (strongest voice signal)
- [mtk](https://github.com/aarontowell/mtk) — Music/email toolkit
- [btk](https://github.com/aarontowell/btk) — Bookmark toolkit
- [ptk](https://github.com/aarontowell/ptk) — Photo toolkit
- [ebk](https://github.com/aarontowell/ebk) — Ebook/reading toolkit

### Persona Enhancement

- [infinigram](https://github.com/aarontowell/infinigram) — Suffix-array n-gram model for probability mixing
- [langcalc](https://github.com/aarontowell/langcalc) — Algebraic language model composition (reference)

### Compliance and Validation

- [longecho](https://github.com/aarontowell/longecho) — ECHO compliance validator

---

*"The ghost is not you. But it echoes you."*
