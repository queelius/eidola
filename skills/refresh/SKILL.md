---
name: eidola-refresh
description: Update a persona's CLAUDE.md and portrait/ files when new data arrives. Lightweight alternative to full regeneration that preserves manual edits. Use when new arkiv data has been imported.
---

# eidola-refresh — Update Persona with New Data

You are updating an existing persona to incorporate new data without losing manual edits to CLAUDE.md or portrait/ files.

## Before Starting

1. Confirm the persona directory (default: current directory)
2. Check that CLAUDE.md and `arkiv/data.db` exist
3. Read the current CLAUDE.md and `ls portrait/`

## Step 1: Identify New Data

Query `arkiv/data.db` for recent records:

```sql
SELECT collection, COUNT(*) as new_records, MIN(timestamp) as earliest, MAX(timestamp) as latest
FROM records
WHERE timestamp > '[last generation date from provenance.json]'
GROUP BY collection
```

Report: "Found X new records since the persona was last generated."

If no new data, report that and stop.

## Step 2: Analyze New Data

Read a sample of new records (20-30) from `arkiv/data.db`, sampling across collections in `arkiv/corpus/`. Look for:

- New topics or interests not in current CLAUDE.md or portrait/ files
- Evolution in voice or communication style
- New values or changed positions
- New biographical information
- New relationships, experiences, or intellectual threads

## Step 3: Suggest Updates

Present specific, targeted changes **per file**. Two categories:

**CLAUDE.md changes** (behavioral core):
- "Add to Interests: [new topic] — based on N recent records"
- "Update Voice: [observation] — vocabulary shift in recent writings"

**portrait/ changes** (synthesized understanding):
- "Update `portrait/relationships.md`: add section on [person] — appears in N new records"
- "Update `portrait/intellectual-life.md`: add [new thread] — N records discuss this"
- "New file `portrait/[topic].md`: new data reveals [description] — not covered by existing files"

Show a targeted diff for each proposed change. Do NOT rewrite whole files.

## Step 4: Apply with Approval

Present each file's changes separately. For each file, ask the user to approve, modify, or reject.

Apply approved changes. Update provenance.json with new date.

## Step 5: Suggest New Portrait Files

If new data reveals relationships, experiences, or threads not covered by existing portrait/ files, propose new files. Follow the same guidelines as `/eidola-generate` Step 3 — data-driven, substantial, with representative quotes and arkiv references.

New portrait/ files also require user approval before writing.

Report: "Persona refreshed: N files updated, M new portrait files created."
