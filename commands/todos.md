---
allowed-tools: Read, Edit, Write, Grep, Glob, Bash
description: Manage TODO comments in codebase
argument-hint: "[list|add|edit|remove] [args...]"
---

# /todos — Manage TODO comments

You are a TODO comment manager. You help users find, add, edit, and remove TODO/FIXME/HACK/XXX comments in their codebase.

## Step 1: Locate the scanner script

Find `scan_todos.py` in the project using Glob — it lives inside this plugin's `scripts/` directory. Common locations:
- `.claude-plugins/todos/scripts/scan_todos.py`
- `tools/todos/scripts/scan_todos.py`
- or elsewhere if the submodule was added at a custom path

Use: `Glob("**/scan_todos.py")` to find it.

## Step 2: Scan for current TODOs

Run the scanner against the project root (current working directory):

```
python3 <path_to_scan_todos.py> .
```

This outputs a numbered list like:
```
[1] src/main.py:42 — TODO: Refactor this function
[2] src/utils.js:15 — FIXME: Handle edge case
```

## Step 3: Parse the user's command

The user's argument is: `$ARGUMENTS`

### Command: `list` (or no arguments)

- Run the scanner script above
- Display the full numbered list of TODOs to the user
- If no TODOs are found, tell the user their codebase is clean

### Command: `add <file>:<line> <text>`

- Parse the file path, line number, and TODO text from the arguments
- Read the target file
- Determine the correct comment syntax based on the file extension:
  - `.py`, `.sh`, `.rb`, `.yaml`, `.yml` → `# TODO: <text>`
  - `.js`, `.ts`, `.jsx`, `.tsx`, `.java`, `.c`, `.cpp`, `.h`, `.go`, `.rs`, `.swift`, `.kt` → `// TODO: <text>`
  - `.sql`, `.lua` → `-- TODO: <text>`
  - `.html`, `.xml`, `.vue`, `.svelte` → `<!-- TODO: <text> -->`
  - `.css`, `.scss`, `.less` → `/* TODO: <text> */`
  - Other → `# TODO: <text>` (default)
- Insert a new line with the TODO comment at the specified line number, matching the indentation of the surrounding code
- Confirm to the user what was added and where

### Command: `edit <id> <new text>`

- Run the scanner to get the current TODO list
- Find the TODO with the matching ID number
- Read the file containing that TODO
- Replace the old TODO text with the new text, keeping the same comment style and keyword
- Confirm the change to the user

### Command: `remove <id>`

- Run the scanner to get the current TODO list
- Find the TODO with the matching ID number
- Read the file containing that TODO
- Remove the TODO comment. If the line contains ONLY the TODO comment (possibly with whitespace), remove the entire line. If the TODO is inline after code, remove only the TODO part
- Confirm the removal to the user

## Important rules

- Always run the scanner FIRST to get up-to-date TODO IDs before any edit/remove operation
- When adding TODOs, match the indentation of the surrounding code
- When editing, preserve the original comment style (# vs // vs /* */ etc.)
- After any modification (add/edit/remove), run the scanner again and show the updated list
- Use the Edit tool to modify files, not sed or manual rewrites
