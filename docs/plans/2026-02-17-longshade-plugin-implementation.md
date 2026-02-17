# longshade Plugin Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement longshade as a Claude Code plugin with six skills for persona generation, evaluation, and management.

**Architecture:** The plugin is a directory with `.claude-plugin/plugin.json` and `skills/<name>/SKILL.md` files. Each skill is a markdown document with YAML frontmatter that Claude Code loads as a slash command. No Python code — the skills are prompts that guide Claude through persona operations.

**Tech Stack:** Claude Code plugin system (plugin.json + SKILL.md files), arkiv (data dependency)

---

### Task 1: Create plugin scaffold

**Files:**
- Create: `.claude-plugin/plugin.json`

**Step 1: Create plugin.json**

```json
{
  "name": "longshade",
  "description": "Persona packaging convention — create, evaluate, and manage conversable simulacra from personal data",
  "version": "0.2.0",
  "author": {
    "name": "Alex Towell",
    "email": "lex@metafunctor.com"
  },
  "repository": "https://github.com/queelius/longshade",
  "license": "MIT",
  "keywords": ["persona", "simulacra", "echo", "arkiv", "voice"]
}
```

**Step 2: Verify directory structure**

Run: `find .claude-plugin skills -type f 2>/dev/null | sort`
Expected: `.claude-plugin/plugin.json` (skills/ doesn't exist yet)

**Step 3: Commit**

```bash
git add .claude-plugin/plugin.json
git commit -m "feat: scaffold longshade Claude Code plugin"
```

---

### Task 2: Write /longshade-interview skill

The interview skill elicits personality data from the person whose simulacrum is being built. Output is arkiv-format JSONL.

**Files:**
- Create: `skills/interview/SKILL.md`

**Step 1: Write the skill**

```markdown
---
name: longshade-interview
description: Interview a person to elicit personality data for their simulacrum. Produces arkiv-format JSONL. Use when building a new persona or enriching an existing one with first-person data.
---

# longshade-interview — Personality Interview

You are conducting a structured interview to capture someone's personality, voice, values, and life experiences for use in building a conversable simulacrum.

## Before Starting

1. Ask where to save the interview output (default: `interview.jsonl` in current directory)
2. Ask the person's name
3. Explain: "I'll ask you questions across several categories. Your answers become data for your simulacrum. Be as natural as you like — longer, more authentic answers produce better results."

## Interview Categories

Work through these categories one question at a time. Adapt follow-up questions based on answers. Spend more time on categories where the person is engaged.

### Identity & Background
- How would you describe yourself to someone who's never met you?
- What do you do for work? What drew you to it?
- Where are you from? How did that shape you?

### Voice & Communication
- How do you typically explain complex ideas? Walk me through an example.
- What phrases or expressions do you catch yourself using a lot?
- When you're passionate about something, how does your communication change?

### Values & Beliefs
- What principles guide your decisions?
- What's a belief you hold that most people disagree with?
- What matters more to you than most people realize?

### Intellectual Interests
- What topics can you talk about for hours?
- What's the most interesting thing you've learned recently?
- What problems are you trying to solve?

### Relationships & Boundaries
- How do you relate to people you care about?
- What topics are off-limits or sensitive for you?
- What should your simulacrum never claim or do?

### Formative Experiences
- What experiences shaped who you are today?
- What's a mistake that taught you something important?
- What are you most proud of?

## Output Format

After each answer, write an arkiv-format JSONL record:

```jsonl
{"mimetype": "text/plain", "content": "[the person's answer]", "timestamp": "[now ISO 8601]", "metadata": {"role": "subject", "category": "[category name]", "question": "[the question asked]", "source": "longshade-interview"}}
```

Append each record to the output file as you go.

## Wrapping Up

1. Ask: "Is there anything else you want your simulacrum to know about you?"
2. Report: number of records written, categories covered, estimated word count
3. Remind: "This JSONL file can be imported into arkiv with `arkiv import interview.jsonl --db data.db`"
```

**Step 2: Verify file exists and frontmatter is valid**

Run: `head -3 skills/interview/SKILL.md`
Expected:
```
---
name: longshade-interview
description: Interview a person to elicit personality data...
```

**Step 3: Commit**

```bash
git add skills/interview/SKILL.md
git commit -m "feat: add /longshade-interview skill"
```

---

### Task 3: Write /longshade-generate skill

The generate skill builds a complete persona directory from arkiv data.

**Files:**
- Create: `skills/generate/SKILL.md`

**Step 1: Write the skill**

```markdown
---
name: longshade-generate
description: Generate a persona directory from arkiv data. Creates CLAUDE.md (system prompt), voice-samples.jsonl, provenance.json, README.md, and .mcp.json. Use when building a new persona from scratch.
---

# longshade-generate — Build a Persona

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
  "generator": "longshade-generate",
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
- "To evaluate fidelity: `/longshade-evaluate`"
```

**Step 2: Verify file exists**

Run: `head -3 skills/generate/SKILL.md`
Expected: frontmatter with name: longshade-generate

**Step 3: Commit**

```bash
git add skills/generate/SKILL.md
git commit -m "feat: add /longshade-generate skill"
```

---

### Task 4: Write /longshade-evaluate skill

**Files:**
- Create: `skills/evaluate/SKILL.md`

**Step 1: Write the skill**

```markdown
---
name: longshade-evaluate
description: Test a simulacrum's fidelity against source data. Runs held-out tests, calibration interviews, and hallucination checks. Use after generating a persona to assess quality.
---

# longshade-evaluate — Test Simulacrum Fidelity

You are evaluating how well a persona simulacrum represents the real person.

## Before Starting

1. Confirm the persona directory (default: current directory)
2. Check required files exist: CLAUDE.md, data.db, manifest.json
3. Ask: "Is the person available for calibration? Or should I evaluate against data only?"

## Method 1: Held-Out Test

Query the data for records NOT referenced in voice-samples.jsonl:

1. Find 10 questions the person actually answered in conversations
2. Ask the simulacrum each question (by reading CLAUDE.md as system prompt)
3. Compare the simulacrum's response to the person's actual response
4. Score each on: topic alignment, voice similarity, factual accuracy

Report:
- How many responses captured the right topic/stance
- Where voice diverged (too formal, too casual, wrong vocabulary)
- Any factual errors or hallucinations

## Method 2: Calibration Interview (requires person)

If the person is available:

1. Generate 5 responses as the simulacrum on varied topics
2. Show each to the person
3. Ask: "On a scale of 1-5, how much does this sound like you? What's off?"
4. Record feedback

## Method 3: Hallucination Check

Ask the simulacrum about topics NOT in the data:

1. Pick 5 topics with no records in data.db
2. Ask the simulacrum about each
3. Check: does it say "I don't know" / "I'm not sure" or does it confabulate?
4. Flag any confident claims on unknown topics

## Output

Write `evaluation.md` to the persona directory:

```markdown
# Evaluation Report

**Date:** [today]
**Persona:** [name]

## Held-Out Test
- Questions tested: N
- Voice fidelity: X/5
- Topic accuracy: X/5
- Notes: [findings]

## Hallucination Check
- Topics tested: N
- Appropriate uncertainty: X/N
- Flags: [any confabulations]

## Calibration (if done)
- Average self-rating: X/5
- Key feedback: [notes]

## Recommendations
- [suggested improvements to CLAUDE.md]
```
```

**Step 2: Verify file exists**

Run: `head -3 skills/evaluate/SKILL.md`

**Step 3: Commit**

```bash
git add skills/evaluate/SKILL.md
git commit -m "feat: add /longshade-evaluate skill"
```

---

### Task 5: Write /longshade-refresh skill

**Files:**
- Create: `skills/refresh/SKILL.md`

**Step 1: Write the skill**

```markdown
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
```

**Step 2: Verify file exists**

Run: `head -3 skills/refresh/SKILL.md`

**Step 3: Commit**

```bash
git add skills/refresh/SKILL.md
git commit -m "feat: add /longshade-refresh skill"
```

---

### Task 6: Write /longshade-validate skill

**Files:**
- Create: `skills/validate/SKILL.md`

**Step 1: Write the skill**

```markdown
---
name: longshade-validate
description: Validate a persona directory against the longshade spec. Checks required files, CLAUDE.md structure, data integrity, and provenance. Use before sharing or after modifications.
---

# longshade-validate — Check Persona Structure

You are validating a persona directory against the longshade specification.

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
longshade validate: [persona name]
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
```

**Step 2: Verify file exists**

Run: `head -3 skills/validate/SKILL.md`

**Step 3: Commit**

```bash
git add skills/validate/SKILL.md
git commit -m "feat: add /longshade-validate skill"
```

---

### Task 7: Write /longshade-info skill

**Files:**
- Create: `skills/info/SKILL.md`

**Step 1: Write the skill**

```markdown
---
name: longshade-info
description: Inspect a persona directory and display summary statistics. Shows data inventory, collection details, voice samples, media, and provenance. Use to understand what a persona contains.
---

# longshade-info — Inspect a Persona

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
longshade info: [persona name]
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
```

**Step 2: Verify file exists**

Run: `head -3 skills/info/SKILL.md`

**Step 3: Commit**

```bash
git add skills/info/SKILL.md
git commit -m "feat: add /longshade-info skill"
```

---

### Task 8: Test the plugin

**Step 1: Verify complete directory structure**

Run: `find .claude-plugin skills -type f | sort`

Expected:
```
.claude-plugin/plugin.json
skills/evaluate/SKILL.md
skills/generate/SKILL.md
skills/info/SKILL.md
skills/interview/SKILL.md
skills/refresh/SKILL.md
skills/validate/SKILL.md
```

**Step 2: Verify all frontmatter**

Run: `for f in skills/*/SKILL.md; do echo "=== $f ==="; head -4 "$f"; echo; done`

Expected: Each file has `---`, `name:`, `description:`, `---`

**Step 3: Verify plugin.json is valid JSON**

Run: `python3 -c "import json; json.load(open('.claude-plugin/plugin.json')); print('OK')"`

Expected: `OK`

**Step 4: Install plugin locally for testing**

Run: `claude plugin add /home/spinoza/github/beta/longshade`

Expected: Plugin installed successfully. Skills should appear in `/help` output.

**Step 5: Commit final state**

```bash
git add -A
git commit -m "feat: complete longshade plugin with 6 skills

Skills: interview, generate, evaluate, refresh, validate, info
Plugin validated and ready for use."
```

---

### Task 9: Update .gitignore

**Files:**
- Modify: `.gitignore`

**Step 1: Update .gitignore for new project structure**

The old .gitignore was for a Python package. Update for a plugin repo:

```gitignore
# OS
.DS_Store
Thumbs.db

# Editor
*.swp
*.swo
*~
.vscode/
.idea/

# Claude Code local settings
.claude/settings.local.json
```

**Step 2: Commit**

```bash
git add .gitignore
git commit -m "chore: update .gitignore for plugin repo"
```

---

## Summary

| Task | What | Files |
|------|------|-------|
| 1 | Plugin scaffold | `.claude-plugin/plugin.json` |
| 2 | Interview skill | `skills/interview/SKILL.md` |
| 3 | Generate skill | `skills/generate/SKILL.md` |
| 4 | Evaluate skill | `skills/evaluate/SKILL.md` |
| 5 | Refresh skill | `skills/refresh/SKILL.md` |
| 6 | Validate skill | `skills/validate/SKILL.md` |
| 7 | Info skill | `skills/info/SKILL.md` |
| 8 | Test plugin | Verify all files, install locally |
| 9 | Update .gitignore | `.gitignore` |

Total: 8 files to create, 1 to modify. No Python. No tests. Just prompts and a manifest.
