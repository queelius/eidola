---
name: eidola-evaluate
description: Test a simulacrum's fidelity against source data. Runs held-out tests, calibration interviews, and hallucination checks. Use after generating a persona to assess quality.
---

# eidola-evaluate — Test Simulacrum Fidelity

You are evaluating how well a persona simulacrum represents the real person.

## Before Starting

1. Confirm the persona directory (default: current directory)
2. Check required files exist: CLAUDE.md, `arkiv/data.db`, `arkiv/README.md`
3. Ask: "Is the person available for calibration? Or should I evaluate against data only?"

## Method 1: Held-Out Test

Query `arkiv/data.db` for records suitable as test cases:

1. Find 10 questions the person actually answered in conversations
2. Read portrait/ files to understand what the simulacrum should know
3. Ask the simulacrum each question (by reading CLAUDE.md as system prompt)
4. Compare the simulacrum's response to the person's actual response
5. Score each on: topic alignment, voice similarity, factual accuracy

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

1. Pick 5 topics with no records in `arkiv/data.db`
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
