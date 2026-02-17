---
name: eidola-validate
description: Validate a persona directory against the eidola spec. Checks required files, CLAUDE.md structure, data integrity, and provenance. Use before sharing or after modifications.
---

# eidola-validate — Check Persona Structure

You are validating a persona directory against the eidola specification.

## Before Starting

Confirm the persona directory to validate (default: current directory).

## Checks

Run all checks and report results:

### Required Files
- [ ] `README.md` exists
- [ ] `CLAUDE.md` exists
- [ ] `data.db` exists and is a valid SQLite database
- [ ] `manifest.json` exists and is valid JSON

### CLAUDE.md Structure
- [ ] Has Identity section (name, background)
- [ ] Has Voice section (communication style)
- [ ] Has Values section
- [ ] Has Boundaries section
- [ ] Has MCP Instructions section (arkiv tool usage)

### Data Integrity
- [ ] `data.db` has a `records` table
- [ ] `data.db` has a `_schema` table
- [ ] Record count matches manifest (if specified)
- [ ] `.mcp.json` exists and references data.db

### Optional Files
- [ ] `provenance.json` exists and has `subject` and `authorized_by` fields
- [ ] `voice-samples.jsonl` exists and contains valid JSONL
- [ ] `evaluation.md` exists
- [ ] `memory/` directory exists
- [ ] `media/` directory exists (if records reference media)
- [ ] `corpus/` directory exists with JSONL files

### ECHO Compliance
- [ ] README.md is self-describing (explains what this is)
- [ ] All data in durable formats (text, JSONL, SQLite)
- [ ] No cloud dependencies required for basic use

## Report

```
eidola validate: [persona name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Required:  [N/4] passed
Structure: [N/5] passed
Data:      [N/4] passed
Optional:  [N/6] present

[PASS/WARN/FAIL] — [summary]
```

PASS = all required checks pass
WARN = required passes but optional items missing
FAIL = required checks failed (list what's missing)
