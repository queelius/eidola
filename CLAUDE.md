# CLAUDE.md

## What eidola Is

A persona packaging convention (SPEC.md) and Claude Code plugin for creating simulacra from personal data.

- **The spec** defines the persona directory convention
- **The plugin** provides skills to generate, validate, and inspect persona directories
- **The output** is an ECHO-compliant directory that IS a Claude Code project

A persona directory contains a CLAUDE.md (system prompt), arkiv data (SQLite + JSONL), and an MCP config. To use it: `cd persona/ && claude`.

## What eidola Is NOT

- Not a Python package — no pip install, no code, no dependencies
- Not a RAG pipeline, embedding system, or retrieval engine
- Not a fine-tuned model or training framework
- Not an application that calls LLM APIs

## Project Structure

```
eidola/
├── .claude-plugin/
│   └── plugin.json            # Claude Code plugin definition
├── hooks/
│   ├── hooks.json             # Hook configuration
│   └── session-start.sh       # Session start hook
├── skills/                    # Plugin skills
│   ├── evaluate/SKILL.md      # /eidola-evaluate
│   ├── generate/SKILL.md      # /eidola-generate
│   ├── info/SKILL.md          # /eidola-info
│   ├── interview/SKILL.md     # /eidola-interview
│   ├── refresh/SKILL.md       # /eidola-refresh
│   └── validate/SKILL.md      # /eidola-validate
├── SPEC.md                    # Persona directory convention
├── README.md                  # What eidola is
├── CLAUDE.md                  # This file
└── docs/plans/                # Design history
```

## Key Principles

1. **The LLM is the intelligence** — Claude Code does the analysis, not custom code
2. **The output is durable** — plain text, JSONL, SQLite. ECHO-compliant.
3. **Light touch** — the spec is minimal, the future will do it better
4. **arkiv is the data layer** — eidola depends on arkiv for data format and MCP

## Dependencies

- [arkiv](../arkiv/) — Universal personal data format (JSONL + SQLite + MCP)
- [Claude Code](https://claude.ai/code) — Intelligence layer (runs the plugin)

## Related Projects

- [arkiv](../arkiv/) — Data layer
- [longecho](../longecho/) — ECHO compliance validator
- [memex](../memex/), [mtk](../mtk/), [btk](../btk/), [ptk](../ptk/), [ebk](../ebk/) — Source toolkits
- [repoindex](../repoindex/), [chartfold](../chartfold/) — Additional data sources
