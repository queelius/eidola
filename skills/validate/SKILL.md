---
name: eidola-validate
description: Validate a persona directory against the eidola v0.3 spec. Checks required files, three-domain structure (arkiv/portrait/memory), CLAUDE.md structure, data integrity, and immutable/mutable boundary. Use before sharing or after modifications.
---

# eidola-validate — Check Persona Structure

You are validating a persona directory against the eidola v0.3 specification.

## Before Starting

Confirm the persona directory to validate (default: current directory).

## Checks

Run all checks and report results:

### Required Files
- [ ] `README.md` exists
- [ ] `CLAUDE.md` exists
- [ ] `arkiv/data.db` exists and is a valid SQLite database
- [ ] `arkiv/README.md` exists and has YAML frontmatter

### CLAUDE.md Structure
- [ ] Has Identity section (name, background)
- [ ] Has Voice section (registers — formal, informal, exploratory)
- [ ] Has Values section
- [ ] Has Boundaries section
- [ ] Has Retrieval Instructions section (arkiv MCP, memory MCP, portrait/ reference)

### Three-Domain Structure
- [ ] `arkiv/` directory exists with `data.db` and `README.md`
- [ ] `portrait/` directory exists with at least one `.md` file
- [ ] `memory/` directory exists
- [ ] `.mcp.json` references both `arkiv/data.db` and `memory/data.db`

### Data Integrity
- [ ] `arkiv/data.db` has a `records` table
- [ ] `arkiv/data.db` has a `_schema` table
- [ ] Record count is non-zero
- [ ] `memory/data.db` exists and is valid SQLite (can be empty)

### Immutable/Mutable Boundary
- [ ] `arkiv/` contains no generated content markers (`metadata.generated: true`)
- [ ] `memory/` records (if any) have `metadata.generated: true`

### Optional Files
- [ ] `provenance.json` exists with `subject` and `authorized_by` fields
- [ ] `evaluation.md` exists
- [ ] `arkiv/corpus/` directory exists with JSONL files
- [ ] `arkiv/media/` directory exists (if records reference media)

### ECHO Compliance
- [ ] README.md is self-describing (explains what this is)
- [ ] All data in durable formats (text, JSONL, SQLite)
- [ ] No cloud dependencies required for basic use

## Report

```
eidola validate: [persona name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Required:   [N/4] passed
Structure:  [N/5] passed
Domains:    [N/4] passed    (arkiv/ portrait/ memory/)
Data:       [N/4] passed
Boundary:   [N/2] passed    (immutable/mutable)
Optional:   [N/4] present

[PASS/WARN/FAIL] — [summary]
```

PASS = all required + structure + domains + data + boundary checks pass
WARN = required passes but optional items missing
FAIL = required checks failed (list what's missing)
