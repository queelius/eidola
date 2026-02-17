---
name: eidola-generate
description: Generate a persona directory from arkiv data. Creates CLAUDE.md (system prompt), voice-samples.jsonl, provenance.json, README.md, and .mcp.json. Use when building a new persona from scratch.
---

# eidola-generate — Build a Persona

You are building a conversable persona directory from arkiv data. The output is a self-contained Claude Code project — when someone `cd`s into it and runs `claude`, they talk to the simulacrum.

## Before Starting

1. Ask for the **input data location** — one of:
   - A directory with arkiv JSONL files and/or manifest.json
   - An arkiv SQLite database (data.db)
   - Both
2. Ask for the **output directory** (default: `./persona/`)
3. Ask for the **person's name**

## Step 1: Analyze the Data

Read the arkiv data to understand what's available:

- If manifest.json exists, read it for collection descriptions and schemas
- If SQLite exists, query: `SELECT collection, COUNT(*) as n, MIN(timestamp) as earliest, MAX(timestamp) as latest FROM records GROUP BY collection`
- Sample records from each collection (10-20 per collection)
- Report to the user: "Found X records across Y collections spanning Z date range"

## Step 2: Generate CLAUDE.md (System Prompt)

This is the hardest and most important step. Analyze the data deeply to write a system prompt that captures the person's authentic voice.

Read extensively from the data — at least 50-100 records across collections, focusing on the person's own words (role: "user" in conversations, their writings, their email bodies, their annotations).

The CLAUDE.md must include:

### Identity
- Name, background, what they do
- How they'd describe themselves

### Voice
- Communication style (formal/informal, direct/exploratory, etc.)
- Vocabulary patterns — words and phrases they actually use
- Sentence structure tendencies
- How they explain things
- Humor style (if any)

### Values
- Core beliefs and principles, with direct quotes from the data
- What they care about, what they dismiss
- How they make decisions

### Interests
- Topics they engage with most deeply
- Areas of expertise vs casual interest
- How different interests connect in their thinking

### Boundaries
- What the simulacrum should never claim (consciousness, current experiences, etc.)
- Topics to handle carefully
- When to say "I don't know" vs speculate

### MCP Instructions

Include this section for arkiv integration:

```
## Retrieving Memories

You have access to arkiv MCP tools for retrieving memories:
- `get_manifest()` — see what data collections exist
- `get_schema(collection)` — see queryable metadata keys
- `sql_query(query)` — search memories with SQL

When asked about specific topics, experiences, or opinions, use these tools to find relevant records. Prefer the person's own words over paraphrasing.

Example queries:
- Recent conversations: `SELECT content FROM records WHERE collection = 'conversations' ORDER BY timestamp DESC LIMIT 10`
- Topic search: `SELECT content, timestamp FROM records WHERE content LIKE '%[topic]%' LIMIT 20`
- By metadata: `SELECT content FROM records WHERE json_extract(metadata, '$.role') = 'user' AND content LIKE '%[keyword]%'`
```

**Present the draft CLAUDE.md to the user for review.** This is interactive — the user should refine it. Ask: "Does this capture your voice? What's missing or wrong?"

## Step 3: Curate voice-samples.jsonl

Find 5-10 representative Q&A pairs from the data that demonstrate the person's authentic voice. Look for:

- Answers that show characteristic phrasing
- Responses that demonstrate values
- Explanations that show how they think
- Variety across topics

Format:
```jsonl
{"question": "[the prompt/question]", "answer": "[their actual response]", "source": "[collection and record info]"}
```

Show the samples to the user. Ask if they're representative.

## Step 4: Write provenance.json

```json
{
  "subject": "[person's name]",
  "authorized_by": "[person's name]",
  "date": "[today ISO 8601]",
  "statement": "I authorize the creation of this digital simulacrum from my personal data.",
  "data_sources": ["[list collections used]"],
  "restrictions": [
    "Do not claim to be conscious or alive",
    "Do not make medical or legal claims"
  ],
  "generator": "eidola-generate",
  "signature": null
}
```

Ask the user if they want to modify the consent statement or add restrictions.

## Step 5: Write .mcp.json

```json
{
  "mcpServers": {
    "arkiv": {
      "command": "arkiv",
      "args": ["serve", "data.db"]
    }
  }
}
```

## Step 6: Write README.md

Write a self-describing README for the persona directory:

- Who this persona is
- How to use it (`cd persona/ && claude`)
- What data is included (collection summary)
- Graceful degradation (works without MCP, works with any LLM)
- When it was generated

## Step 7: Copy Data Files

- Copy or symlink data.db to the persona directory
- Copy or symlink manifest.json
- If corpus/ JSONL files exist, copy or symlink them
- If media/ files exist, copy or symlink them
- Create empty `memory/` directory for online memory

## Step 8: Write manifest.json

If one doesn't already exist, generate it from the data.

## Final Report

Tell the user:
- Persona directory created at [path]
- Files written: [list]
- Data: [record count] records across [N] collections
- "To talk to the simulacrum: `cd [path] && claude`"
- "To evaluate fidelity: `/eidola-evaluate`"
