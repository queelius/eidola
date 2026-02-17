---
name: longshade-refresh
description: Update a persona's CLAUDE.md when new data arrives. Lightweight alternative to full regeneration that preserves manual edits. Use when new arkiv data has been imported.
---

# longshade-refresh — Update Persona with New Data

You are updating an existing persona to incorporate new data without losing manual edits to CLAUDE.md.

## Before Starting

1. Confirm the persona directory (default: current directory)
2. Check that CLAUDE.md and data.db exist
3. Read the current CLAUDE.md

## Step 1: Identify New Data

Query data.db for recent records:

```sql
SELECT collection, COUNT(*) as new_records, MIN(timestamp) as earliest, MAX(timestamp) as latest
FROM records
WHERE timestamp > '[last generation date from provenance.json]'
GROUP BY collection
```

Report: "Found X new records since the persona was last generated."

If no new data, report that and stop.

## Step 2: Analyze New Data

Read a sample of new records (20-30). Look for:

- New topics or interests not in current CLAUDE.md
- Evolution in voice or communication style
- New values or changed positions
- New biographical information

## Step 3: Suggest Updates

Present specific, targeted changes to CLAUDE.md:

- "Add to Interests: [new topic] — based on N recent conversations"
- "Update Voice: [observation] — vocabulary shift in recent writings"
- "Add to Values: [new principle] — expressed in [specific record]"

**Do NOT rewrite the whole file.** Show diffs or additions only.

## Step 4: Apply with Approval

For each suggested change, ask the user to approve, modify, or reject.

Apply approved changes. Update provenance.json with new date.

## Step 5: Update voice-samples.jsonl (optional)

If new data contains particularly representative Q&A pairs, suggest adding them.

Report: "CLAUDE.md updated with N changes. Persona refreshed."
