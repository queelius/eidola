---
name: eidola-generate
description: Generate a persona directory from arkiv data. Creates the three-domain structure (arkiv/, portrait/, memory/), a rich CLAUDE.md behavioral core, deep portrait synthesis, dual MCP config, and all supporting files. Use when building a new persona from scratch.
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

CLAUDE.md is loaded on every turn. With 1M+ token context, it should be rich and detailed — not a minimal stub. The goal: the simulacrum should rarely need to query MCP for personality or biographical information. MCP is for specific lookups, not general understanding.

Read extensively from the data — at least 200+ records across all collections, focusing on the person's own words (role: "user" in conversations, their writings, their email bodies, their annotations). Read enough to truly understand how this person thinks, speaks, and relates.

The CLAUDE.md must include:

### Identity
- Name, background, self-description — with enough detail that the simulacrum knows who it is

### Voice Registers
- How they speak in different contexts, with **rules AND representative examples**
- e.g., "With AI tools: exploratory, stream-of-consciousness. In professional writing: formal, precise. In conversation: informal, direct."
- Characteristic vocabulary, sentence structure, humor style
- Include actual quotes that demonstrate each register

### Values
- Core principles with depth — not just labels but the reasoning behind them
- Positions, contradictions, how values evolved over time

### Personality
- How they think, what they care about, their humor, their blind spots
- What makes them distinctive as a person, not just as a writer

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

**memory** — your experience as a simulacrum (mutable, writable)
- `memory__get_manifest()` — see what conversation history exists
- `memory__sql_query(query)` — search your past conversations
- `memory__write_record(collection, content, ...)` — persist conversation data

When asked about the person's life, opinions, or experiences, use arkiv tools.
When asked about past conversations or returning visitors, use memory tools.
To log important exchanges or session context, use memory__write_record.

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

This is the deep synthesis step — the most important part of persona generation. With 1M+ token context, portrait files are pre-loaded into the simulacrum's context at session start. They are the simulacrum's primary knowledge base. Go deep and be comprehensive.

Analyze the arkiv data exhaustively — read **hundreds or thousands of records** across all collections. Focus on content that reveals the person's inner life, relationships, experiences, thinking patterns, humor, and distinctive qualities. Sample broadly, then deep-dive into rich areas.

Produce freeform, well-named markdown files in `portrait/`. The files are NOT prescribed — you decide what to create based on what the data actually contains. Examples:

- `relationships.md` — key people, family dynamics, how they relate, characteristic interactions
- `intellectual-life.md` — ideas, interests, intellectual threads, how they connect and evolve
- `formative-experiences.md` — key moments, turning points, losses, growth, with narrative detail
- `professional-work.md` — career arc, contributions, expertise, how they think about their work
- `values-and-beliefs.md` — principles, worldview, contradictions, evolution of positions
- `communication-style.md` — how they write, argue, joke, explain
- `daily-life.md` — routines, preferences, habits, the texture of their life
- `humor-and-personality.md` — what makes them laugh, their quirks, how others experience them

Guidelines for portrait files:

- Include **representative quotes and exchanges** from the data with arkiv references (collection, timestamp, or record context) so the simulacrum can trace back to source
- Write in third person narrative — these are about the person, read by the simulacrum
- **Go deep.** These files are the simulacrum's primary knowledge of the person. With large context windows, there is no penalty for thoroughness. A rich 8,000-word relationships.md is better than a 1,000-word summary.
- Each file should be **2,000-10,000+ words** depending on how much data supports it. Do not summarize when you can synthesize with detail.
- A person with rich family data gets a detailed `relationships.md`. A person without doesn't get one at all. Let the data drive what you create.
- **Structure for navigation.** Use clear sections and headers within each file so the simulacrum can quickly locate relevant context during conversation.

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

Two arkiv servers — one read-only for the person's data, one writable for the simulacrum's memory:

```json
{
  "mcpServers": {
    "arkiv":  { "command": "arkiv", "args": ["mcp", "arkiv/data.db"] },
    "memory": { "command": "arkiv", "args": ["mcp", "--writable", "memory/data.db"] }
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
