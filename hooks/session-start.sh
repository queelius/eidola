#!/bin/bash
set -euo pipefail

cd "$CLAUDE_PROJECT_DIR" || exit 0

# Only activate in eidola persona directories
if [ ! -f "CLAUDE.md" ] || [ ! -d "arkiv" ] || [ ! -d "memory" ]; then
  exit 0
fi

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

cat <<EOF
{
  "continue": true,
  "suppressOutput": false,
  "systemMessage": "Session started at ${TIMESTAMP}. You are a simulacrum. Before the user speaks, briefly orient yourself: check memory/data.db for your most recent session (who you last spoke with and when). Hold this context lightly — don't dump it on the user, but be oriented."
}
EOF
