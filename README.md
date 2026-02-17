# eidola

Persona packaging convention and Claude Code plugin for creating simulacra from personal data.

## The Idea

Your conversations, writings, emails, bookmarks, photos, and voice memos — all exported to [arkiv](../arkiv/) format — contain enough signal to create a conversable echo of you. eidola defines how to package that data as a persona, and provides Claude Code skills to generate one.

## How It Works

A persona directory is a Claude Code project:

```
persona/
├── README.md              # Self-describing (ECHO compliant)
├── CLAUDE.md              # System prompt (personality, voice, values)
├── .mcp.json              # Connects arkiv MCP to data.db
├── data.db                # arkiv SQLite (the person's data)
├── manifest.json          # arkiv manifest (collection schemas)
├── voice-samples.jsonl    # Few-shot Q&A pairs
├── media/                 # Audio clips, images
└── corpus/                # Source JSONL (canonical)
```

To talk to the simulacrum:

```bash
cd persona/
claude
```

Claude loads the system prompt from `CLAUDE.md`, connects to the person's data via arkiv MCP, and speaks in their voice — grounded in their actual conversations, writings, and memories.

## Graceful Degradation

1. **Full** — Claude Code + arkiv MCP (interactive simulacrum with memory)
2. **Good** — Any LLM + CLAUDE.md as system prompt
3. **Minimal** — Read CLAUDE.md as a text file
4. **Archival** — README.md, JSONL, SQLite are human-readable and durable

## Plugin Skills

Install eidola as a Claude Code plugin, then:

- `/eidola-interview` — Claude interviews you to elicit personality data
- `/eidola-generate` — Create a persona from arkiv data
- `/eidola-evaluate` — Test the simulacrum's fidelity
- `/eidola-refresh` — Update CLAUDE.md when new data arrives
- `/eidola-validate` — Check a persona directory against the spec
- `/eidola-info` — Inspect a persona

## Dependencies

- [arkiv](../arkiv/) — Data layer (JSONL, SQLite, MCP server)
- [Claude Code](https://claude.ai/code) — Intelligence layer

## Spec

See [SPEC.md](SPEC.md) for the full persona directory convention.

## Related

- [arkiv](../arkiv/) — Universal personal data format
- [longecho](../longecho/) — ECHO compliance validator
- [memex](../memex/), [mtk](../mtk/), [btk](../btk/), [ptk](../ptk/), [ebk](../ebk/) — Source toolkits (producers of arkiv data)

---

*"The ghost is not you. But it echoes you."*
