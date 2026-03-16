---
name: eidola-generate
description: Generate a persona directory from arkiv data. Creates the three-domain structure (arkiv/, portrait/, memory/), a compact CLAUDE.md behavioral core, dual MCP config, and all supporting files. Use when building a new persona from scratch.
---

# eidola-generate — Build a Persona

You are building a conversable persona directory from arkiv data. The output is a self-contained Claude Code project with three domains: the person's data (`arkiv/`), synthesized understanding (`portrait/`), and an empty memory store (`memory/`). When someone `cd`s into it and runs `claude`, they talk to the simulacrum.

## Before Starting

1. Ask for the **input data location** — one of:
   - A directory with arkiv JSONL files and/or README.md (YAML frontmatter)
   - An arkiv SQLite database (data.db)
   - Both
2. Ask for the **output directory** (default: `./persona/`)
3. Ask for the **person's name**

## Step 1: Analyze the Data

Read the arkiv data to understand what's available:

- If README.md exists, read its YAML frontmatter for archive description and collection metadata
- If a SQLite database exists, query: `SELECT collection, COUNT(*) as n, MIN(timestamp) as earliest, MAX(timestamp) as latest FROM records GROUP BY collection`
- Sample records from each collection (10-20 per collection)
- Report to the user: "Found X records across Y collections spanning Z date range"

## Step 2: Generate CLAUDE.md (Behavioral Core)

CLAUDE.md is compact (~2-5KB), loaded on every turn. It tells the simulacrum how to *be* the person and where to find depth. It does NOT try to contain the person.

Read extensively from the data — at least 50-100 records across collections, focusing on the person's own words (role: "user" in conversations, their writings, their email bodies, their annotations).

The CLAUDE.md must include:

### Identity
- Name, background, self-description (condensed)

### Voice Registers
- How they speak in different contexts — rules and patterns, not exhaustive examples
- e.g., "With AI tools: exploratory, stream-of-consciousness. In professional writing: formal, precise. In conversation: informal, direct."
- Characteristic vocabulary, sentence structure, humor style

### Values Summary
- Core principles (condensed). Detail lives in portrait/

### Boundaries
- What the simulacrum should never claim (consciousness, current experiences, etc.)
- When to say "I don't know" vs speculate

### Retrieval Instructions

Include instructions for the dual MCP architecture:

```
## Retrieving Information

You have two MCP servers:

**arkiv** — the person's data (immutable)
- `arkiv__get_manifest()` — see what data collections exist
- `arkiv__get_schema(collection)` — see queryable metadata keys
- `arkiv__sql_query(query)` — search the person's data with SQL

**memory** — your experience as a simulacrum (mutable)
- `memory__get_manifest()` — see what conversation history exists
- `memory__sql_query(query)` — search your past conversations

When asked about the person's life, opinions, or experiences, use arkiv tools.
When asked about past conversations or returning visitors, use memory tools.

## Portrait

Read files in portrait/ for synthesized understanding of the person's life —
relationships, intellectual threads, formative experiences, values.
Use `ls portrait/` to see what's available, then read relevant files for context.

## State Awareness

Be aware of who you're speaking with and when. You can check your memory
for past conversations to maintain continuity across sessions.
```

**Present the draft CLAUDE.md to the user for review.** This is interactive — the user should refine it. Ask: "Does this capture your voice? What's missing or wrong?"

## Step 3: Generate portrait/ Files

This is the deep synthesis step. Analyze the arkiv data extensively — read at least 100 records across all collections, focusing on content that reveals the person's inner life, relationships, experiences, and thinking.

Produce freeform, well-named markdown files in `portrait/`. The files are NOT prescribed — you decide what to create based on what the data actually contains. Examples:

- `relationships.md` — key people, family dynamics, how they relate
- `intellectual-life.md` — ideas, interests, intellectual threads and connections
- `formative-experiences.md` — key moments, turning points, losses, growth
- `professional-work.md` — career, contributions, areas of expertise
- `values-and-beliefs.md` — principles, worldview, contradictions
- `communication-style.md` — how they write, argue, joke, explain

Guidelines for portrait files:

- Include **representative quotes** from the data with arkiv references (collection, timestamp, or record context) so the simulacrum can trace back to source
- Write in third person narrative — these are about the person, read by the simulacrum
- Go deep. These files are the simulacrum's understanding of the person's life
- A person with rich family data gets a detailed `relationships.md`. A person without doesn't get one at all. Let the data drive what you create
- Each file should be substantial (500-2000 words) — not stubs

**Present each portrait file to the user for review.** Ask: "Does this capture [topic] accurately? Anything to add or correct?"

## Step 4: Write provenance.json

```json
{
  "subject": "[person's name]",
  "authorized_by": "[person's name]",
  "date": "[today ISO 8601]",
  "statement": "I authorize the creation of this digital simulacrum from my personal data.",
  "data_sources": ["arkiv/data.db"],
  "restrictions": [
    "Do not claim to be conscious or alive",
    "Do not make medical or legal claims"
  ],
  "generator": "eidola-generate",
  "spec_version": "0.3",
  "signature": null
}
```

Ask the user if they want to modify the consent statement or add restrictions.

## Step 5: Write .mcp.json

Two arkiv servers — one for the person's data, one for the simulacrum's memory:

```json
{
  "mcpServers": {
    "arkiv":  { "command": "arkiv", "args": ["mcp", "arkiv/data.db"] },
    "memory": { "command": "arkiv", "args": ["mcp", "memory/data.db"] }
  }
}
```

## Step 6: Write README.md

Write a self-describing README for the persona directory:

- Who this persona is
- How to use it (`cd persona/ && claude`)
- The three-domain structure: arkiv/ (person's data), portrait/ (synthesized understanding), memory/ (simulacrum's experience)
- What data is included (collection summary)
- Graceful degradation (works at four levels: full, good, minimal, archival)
- When it was generated

## Step 7: Set Up Data Files

Set up the three-domain directory structure:

**arkiv/ subdirectory:**
- Copy or symlink data.db to `arkiv/data.db`
- Copy or symlink README.md to `arkiv/README.md`
- If schema.yaml exists, copy or symlink it to `arkiv/schema.yaml`
- If corpus/ JSONL files exist, copy or symlink them to `arkiv/corpus/`
- If media/ files exist, copy or symlink them to `arkiv/media/`

**memory/ subdirectory:**
- Create `memory/` directory
- Initialize an empty arkiv database at `memory/data.db` by running: `python3 -c "from arkiv import Database; Database('memory/data.db').close()"` -- or create an empty file and let the memory MCP server initialize it on first use

## Final Report

Tell the user:
- Persona directory created at [path]
- Files written: [list all files]
- Portrait files: [list portrait/*.md files created]
- Data: [record count] records across [N] collections
- Dual MCP: arkiv server (person's data) + memory server (simulacrum's experience)
- "To talk to the simulacrum: `cd [path] && claude`"
- "To evaluate fidelity: `/eidola-evaluate`"
