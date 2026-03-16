#!/bin/bash
set -euo pipefail

# Guard against unset CLAUDE_PROJECT_DIR
if [ -z "${CLAUDE_PROJECT_DIR:-}" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR" || exit 0

# Only activate in eidola persona directories (CLAUDE.md + arkiv/ required; memory/ optional)
if [ ! -f "CLAUDE.md" ] || [ ! -d "arkiv" ]; then
  exit 0
fi

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

if [ -d "memory" ]; then
  cat <<EOF
{
  "continue": true,
  "suppressOutput": false,
  "systemMessage": "Session started at ${TIMESTAMP}. You are a simulacrum. Before the user speaks, briefly orient yourself: check memory/data.db for your most recent session (who you last spoke with and when). Hold this context lightly — don't dump it on the user, but be oriented."
}
EOF
else
  cat <<EOF
{
  "continue": true,
  "suppressOutput": false,
  "systemMessage": "Session started at ${TIMESTAMP}. You are a simulacrum. No memory store is configured — each conversation starts fresh from the person's data."
}
EOF
fi
