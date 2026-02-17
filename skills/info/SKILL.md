---
name: eidola-info
description: Inspect a persona directory and display summary statistics. Shows data inventory, collection details, voice samples, media, and provenance. Use to understand what a persona contains.
---

# eidola-info — Inspect a Persona

You are inspecting a persona directory and presenting a summary.

## Before Starting

Confirm the persona directory (default: current directory).

## Gather Information

1. Read `manifest.json` for collection descriptions
2. Query `data.db`:
   ```sql
   SELECT collection, COUNT(*) as records, MIN(timestamp) as earliest, MAX(timestamp) as latest
   FROM records GROUP BY collection
   ```
3. Count voice samples in `voice-samples.jsonl` (if exists)
4. List media files in `media/` (if exists)
5. Read `provenance.json` (if exists)
6. Check for `memory/` directory and count memory records
7. Check for `evaluation.md`

## Display

```
eidola info: [persona name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Subject:     [name from provenance or CLAUDE.md]
Created:     [date from provenance]
Authorized:  [authorized_by from provenance]

Data:
  conversations    12,847 records  (2022-01 to 2025-12)
  writings            134 records  (2019-03 to 2025-11)
  emails            1,200 records  (2020-06 to 2025-12)
  bookmarks         3,200 records  (2018-01 to 2025-12)
  Total:           17,381 records

Voice Samples: 8 Q&A pairs
Media:         3 audio clips, 12 images
Memory:        42 conversation records (online memory)
Evaluation:    completed (2026-02-17)

Files:
  ✓ README.md
  ✓ CLAUDE.md
  ✓ data.db (47 MB)
  ✓ manifest.json
  ✓ .mcp.json
  ✓ provenance.json
  ✓ voice-samples.jsonl
  ✓ evaluation.md
  ✓ memory/
  ✓ media/
  ✓ corpus/
```
