#!/usr/bin/env bash
# Remove tododo symlinks from ~/.claude/.
set -euo pipefail

COMMANDS_DIR="${HOME}/.claude/commands"
SKILLS_DIR="${HOME}/.claude/skills"

echo "Uninstalling tododo..."

if [ -L "${COMMANDS_DIR}/tododo.md" ]; then
    rm "${COMMANDS_DIR}/tododo.md"
    echo "  removed command"
fi

if [ -L "${SKILLS_DIR}/tododo" ]; then
    rm "${SKILLS_DIR}/tododo"
    echo "  removed skill"
fi

echo "Done."
