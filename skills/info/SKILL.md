---
name: eidola-info
description: Inspect a persona directory and display summary statistics. Shows arkiv data inventory, portrait files, memory session stats, and provenance. Use to understand what a persona contains.
---

# eidola-info — Inspect a Persona

You are inspecting a persona directory and presenting a summary across its three domains: arkiv (immutable data), portrait (synthesized understanding), and memory (mutable experience).

## Before Starting

Confirm the persona directory (default: current directory).

## Gather Information

1. Read `provenance.json` (if exists) for subject name, date, and authorization
2. Read `arkiv/manifest.json` for collection descriptions
3. Query `arkiv/data.db`:
   ```sql
   SELECT collection, COUNT(*) as records, MIN(timestamp) as earliest, MAX(timestamp) as latest
   FROM records GROUP BY collection
   ```
4. List `portrait/` files and their sizes (if directory exists)
5. Query `memory/data.db` for session stats (if file exists and is non-empty):
   ```sql
   SELECT COUNT(DISTINCT json_extract(metadata, '$.session_id')) as sessions,
          COUNT(DISTINCT json_extract(metadata, '$.interlocutor')) as interlocutors,
          MIN(timestamp) as earliest, MAX(timestamp) as latest
   FROM records
   ```
6. Check for `evaluation.md`
7. Check existence and sizes of all expected files

## Display

Present the three-domain view:

```
eidola info: [persona name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Subject:     [name]
Created:     [date from provenance]
Authorized:  [authorized_by]

Arkiv Data (immutable):
  conversations    12,847 records  (2022-01 to 2025-12)
  writings            134 records  (2019-03 to 2025-11)
  Total:           17,381 records

Portrait:
  relationships.md          (4.2 KB)
  intellectual-life.md      (6.1 KB)
  formative-experiences.md  (3.8 KB)

Memory (mutable):
  Sessions:      23
  Interlocutors: 4
  Date range:    2026-02 to 2026-02

Files:
  ✓ README.md
  ✓ CLAUDE.md
  ✓ .mcp.json
  ✓ provenance.json
  ✓ evaluation.md
  ✓ arkiv/data.db (47 MB)
  ✓ arkiv/manifest.json
  ✓ portrait/ (3 files)
  ✓ memory/data.db (1.2 MB)
```

### Notes

- If provenance.json is missing, show "unknown" for Subject/Created/Authorized
- If portrait/ is empty or missing, show "Portrait: (none)"
- If memory/data.db is missing or empty, show "Memory: (none)"
- In the Files section, use ✗ for missing required files (README.md, CLAUDE.md, arkiv/data.db, arkiv/manifest.json)
- Show file sizes for databases and portrait files
- Format record counts with comma separators for readability
- Format dates as YYYY-MM
