---
allowed-tools: Read, Edit, Write, Grep, Glob, Bash
description: Manage and execute TODO comments in codebase
argument-hint: "[list|edit|remove|run|explore] [args...]"
---

# /tododo — Manage TODO comments

You are a TODO comment manager. Help users find, edit, remove, and execute TODO/FIXME/HACK/XXX comments in their codebase.

## Scanner

The scanner path is stored in `~/.claude/tododo_root` by the installer. Always resolve it via Bash before running:

```bash
TODODO_ROOT=$(cat ~/.claude/tododo_root)
python3 "$TODODO_ROOT/scripts/scan_todos.py" .
```

For the `run` and `explore` commands, use extended context:

```bash
TODODO_ROOT=$(cat ~/.claude/tododo_root)
python3 "$TODODO_ROOT/scripts/scan_todos.py" --context 5 .
```

Output format:
```
[1] src/main.py:42 — TODO: Refactor this function
[2] src/utils.js:15 — FIXME: Handle edge case
```

## Command: `$ARGUMENTS`

### `list` (or no arguments)

- Run the scanner
- Display the full numbered list of TODOs to the user
- If no TODOs are found, tell the user their codebase is clean

### `edit <id> <new text>`

1. Run the scanner to get current TODO list
2. Find the TODO with the matching ID number
3. Read the file containing that TODO
4. Replace the TODO text with the new text, keeping the same comment style and keyword
5. Confirm the change to the user, re-scan and show updated list

### `remove <id>`

1. Run the scanner to get current TODO list
2. Find the TODO with the matching ID number
3. Read the file containing that TODO
4. Remove the TODO comment:
   - If the line contains ONLY the TODO comment → remove the entire line
   - If the TODO is inline after code → remove only the TODO part
5. Confirm the removal, re-scan and show updated list

### `run [id...]`

Execute (implement) TODO items — do what the TODO describes, then remove the comment.

1. Run the scanner with `--context 5`
2. If specific IDs provided (e.g. `run 1 3`) → work only on those
   If NO IDs provided → display the list and ask which TODOs to execute
3. For each selected TODO, in order:
   a. Read the full file for complete context
   b. Implement what the TODO comment describes
   c. Remove the TODO comment line after successful implementation
   d. Re-read the file before the next TODO (line numbers shift after each edit)
4. Re-scan and show a summary: which TODOs were implemented, files modified, updated list

Skip any TODO that is too vague to implement safely.

### `explore [id...]`

Analyze TODOs, ask clarifying questions for vague ones, and rewrite their text with a concrete implementation plan.

1. Scan with `--context 5`
2. Select TODOs to explore:
   - IDs provided (e.g. `explore 1 3`) → work only on those
   - No IDs → explore all
3. For each selected TODO, in order:
   a. Read the full file to understand the surrounding code
   b. Assess the TODO: Is the intent clear? Is there enough context to implement it?
   c. If the TODO is vague or ambiguous — ask the user a focused clarifying question before proceeding
   d. Formulate a concrete, step-by-step implementation plan for this TODO
   e. Rewrite the TODO text in the code to include the plan: what exactly needs to be done, any relevant details or constraints discovered from the code
   f. Re-read the file before the next TODO (line numbers shift after each edit)
4. After all selected TODOs are processed, show a summary:
   - Which TODOs were updated
   - The updated TODO list

**Goal:** after `explore`, every TODO should be specific enough that `run` can implement it without asking any questions.

**Rewriting style:** keep the comment concise but actionable. Example:
- Before: `# TODO: fix parsing`
- After: `# TODO: fix parsing — handle empty string input in parse_query(); currently raises KeyError on line 47`

## Rules

- Always run the scanner FIRST to get up-to-date TODO IDs before any edit/remove
- Preserve the original comment style when editing (`#`, `//`, `/* */`, `--`, `<!-- -->`, etc.)
- Use the Edit tool to modify files — never sed, awk, or manual rewrites
- Re-scan after any modification and show the updated list
- Re-read files between sequential `run` edits to account for line number shifts
