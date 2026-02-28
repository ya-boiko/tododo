#!/usr/bin/env bash
# Install tododo globally for the current user.
# Symlinks the command and skill into ~/.claude/ so /tododo and the skill
# are available in every Claude Code session.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMANDS_DIR="${HOME}/.claude/commands"
SKILLS_DIR="${HOME}/.claude/skills"

echo "Installing tododo..."

mkdir -p "$COMMANDS_DIR" "$SKILLS_DIR"

rm -f "${COMMANDS_DIR}/tododo.md"
ln -s "${SCRIPT_DIR}/commands/tododo.md" "${COMMANDS_DIR}/tododo.md"
echo "  command → ${COMMANDS_DIR}/tododo.md"

rm -f "${SKILLS_DIR}/tododo"
ln -s "${SCRIPT_DIR}/skills/tododo" "${SKILLS_DIR}/tododo"
echo "  skill   → ${SKILLS_DIR}/tododo"

echo "${SCRIPT_DIR}" > "${HOME}/.claude/tododo_root"
echo "  root    → ${HOME}/.claude/tododo_root"

echo ""
echo "Done. /tododo is now available in all Claude Code sessions."
echo "To update: cd '${SCRIPT_DIR}' && git pull"
echo "To uninstall: ${SCRIPT_DIR}/uninstall.sh"
