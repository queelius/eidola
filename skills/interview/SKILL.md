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
