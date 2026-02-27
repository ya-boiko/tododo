---
name: tododo
description: This skill should be used when the user asks to "show TODOs", "list TODO comments", "find all TODOs", "edit a TODO", "fix a TODO", "remove a TODO", "run TODO #N", "implement a TODO", or mentions managing TODO/FIXME/HACK/XXX comments in their codebase.
---

# Tododo — TODO Comment Manager

Manage TODO/FIXME/HACK/XXX comments across a codebase: list them by number, edit their text, remove them, and execute (implement) what they describe. Uses a bundled Python scanner that finds all TODO-style comments while respecting `.gitignore`.

## Scanner

The scanner is bundled with this plugin. Claude Code sets `CLAUDE_PLUGIN_ROOT` to the plugin's install directory, so the path is always known:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/scan_todos.py" .
```

Extended context (for `run`):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/scan_todos.py" --context 5 .
```

## Scanning for TODOs

Standard scan (2 lines of context around each match):
```bash
python3 scan_todos.py .
```

Extended scan for implementation context:
```bash
python3 scan_todos.py --context 5 .
```

Output format:
```
[1] src/main.py:42 — TODO: Refactor this function
    |  40: def process():
    |  41:     result = []
    |> 42:     # TODO: Refactor this function
    |  43:     return result
    |  44:

[2] src/utils.js:15 — FIXME: Handle null edge case
```

The `[N]` index is positional — it resets on every scan run and shifts whenever files are modified. Always re-scan immediately before referencing an ID.

## Operations

### list

Show all TODO comments with their IDs and locations.

1. Run the scanner: `python3 scan_todos.py .`
2. Display the numbered list
3. If no TODOs found, report that the codebase is clean

### edit `<id> <new text>`

Change the text of an existing TODO comment while keeping its style and keyword.

1. Run the scanner to get current IDs and locations
2. Find the entry matching `<id>`
3. Read the file at the reported path
4. Replace the text after the keyword with `<new text>`, preserving:
   - Comment prefix (`#`, `//`, `/*`, `--`, `<!--`, etc.)
   - Keyword (`TODO`, `FIXME`, `HACK`, or `XXX`)
   - Colon if present
5. Save with the Edit tool
6. Confirm the change, then re-scan and display the updated list

Example: `edit 2 Validate input and raise ValueError` changes only the text; the original `# FIXME:` prefix stays intact.

### remove `<id>`

Delete a TODO comment from source code.

1. Run the scanner to get current IDs and locations
2. Find the entry matching `<id>`
3. Read the file at the reported path
4. Remove the comment using one of two strategies:
   - **Standalone line** (`    # TODO: fix this` with nothing else on the line) → delete the entire line
   - **Inline comment** (`result = compute()  # TODO: cache this`) → strip only the TODO portion, preserving the code before it
5. Save with the Edit tool
6. Confirm the removal, then re-scan and display the updated list

### run `[id...]`

Implement what a TODO describes, then remove the comment once done.

1. Scan with extended context: `python3 scan_todos.py --context 5 .`
2. Determine which TODOs to implement:
   - IDs specified (e.g. `run 1 3`) → work only on those
   - No IDs → display the list and ask the user which ones to execute
3. For each selected TODO, in order:
   a. Read the full file for complete context
   b. Implement the described change — write the actual code, add the missing logic, fix the bug
   c. Remove the TODO comment line after successful implementation:
      - Whole line if it contains only the comment
      - Inline portion only if the comment follows code
   d. Re-read the file before the next TODO in the same file (line numbers shift after each edit)
4. After all TODOs are processed, re-scan and show a summary:
   - Which TODOs were implemented
   - Which files were modified
   - Updated TODO list

Skip any TODO that is too vague to implement safely; report which were skipped and why.

## Rules

**Scan first.** Always run the scanner immediately before any edit or remove operation. IDs shift whenever a file changes.

**Re-scan after changes.** After every modification, run the scanner again and show the updated list.

**Preserve comment style.** When editing, keep the original comment prefix and keyword exactly as found. `// FIXME:` stays `// FIXME:`, not `# FIXME:` or `// TODO:`.

**Edit tool only.** Use the Edit tool for all file changes — never sed, awk, or string replacement scripts.

**Re-read between run steps.** When implementing multiple TODOs sequentially, read the file fresh before each one to get accurate line numbers.

## Edge Cases

**Vague TODOs.** If a TODO says something like `# TODO: fix this`, ask the user for clarification before attempting implementation.

**Multiple TODOs in the same file.** Process them top-to-bottom. Re-read the file before each subsequent edit to account for line shifts.

**Inline TODOs.** When removing `result = compute()  # TODO: cache this result`, leave `result = compute()` intact — strip only from the comment marker onward.

**Block comment TODOs.** When removing a TODO from inside a `/* ... */` or `<!-- ... -->` block that contains other content, preserve the surrounding block comment structure.

## Additional Resources

### Reference Files

- **`references/scanner.md`** — CLI options, supported comment styles, file filtering rules, skip lists, and output format details
