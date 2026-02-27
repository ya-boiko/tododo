# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Conventions

- **Language**: Python 3.10+ only
- **Dependencies**: stdlib only — no pip, no venv, no external packages
- **Commits**: conventional commits format (`feat:`, `fix:`, `refactor:`, `style:`, `docs:`)
- **Never** add `Co-authored-by` to commits
- **Testing**: no test framework — verify changes by running `python3 scripts/scan_todos.py .` directly
- **File edits**: always use the Edit tool, never sed/awk/manual rewrites
- **Config**: `.claude/` is gitignored — local settings are never committed

## Project Overview

This is `tododo`, a Claude Code plugin that provides the `/tododo` slash command for managing TODO/FIXME/HACK/XXX comments in codebases. Users can list, edit, remove, and execute TODO items through Claude.

## Architecture

The plugin consists of three main components:

1. **Plugin Manifest** (`.claude-plugin/plugin.json`): Defines plugin metadata (name, version, author)

2. **Command Definition** (`commands/tododo.md`):
   - Frontmatter declares allowed tools and argument hints
   - Contains the full prompt that Claude receives when `/tododo` is invoked
   - Defines the command interface: `list`, `edit`, `remove`, `run`

3. **Scanner Script** (`scripts/scan_todos.py`):
   - Python 3.10+ script that finds TODO comments in project files
   - Uses `git ls-files` to respect `.gitignore` (falls back to manual walk if not a git repo)
   - Outputs numbered list: `[1] file.py:42 — TODO: description`
   - Supports `--context N` flag to show surrounding code lines

### How the plugin system works

When a user types `/tododo` in a Claude Code conversation:
1. Claude Code loads `commands/tododo.md` and substitutes `$ARGUMENTS` with the user's input
2. The entire markdown content becomes the system prompt for that turn
3. Claude then locates and executes `scan_todos.py` to get the current TODO list
4. Claude performs the requested operation (list/edit/remove/run) using Read/Edit/Write tools

## Development Commands

### Test the scanner directly

```bash
# Scan current directory for TODOs
python3 scripts/scan_todos.py .

# Show 5 lines of context around each TODO
python3 scripts/scan_todos.py --context 5 .

# Scan a specific directory
python3 scripts/scan_todos.py /path/to/project
```

### Testing the command

To test changes to the command definition or scanner:
1. Edit `commands/tododo.md` or `scripts/scan_todos.py`
2. In Claude Code, use `/tododo` — changes are picked up immediately
3. For scanner changes, run the Python script directly first to verify output format

## Comment Style Mapping

The scanner (`scan_todos.py`) recognizes these comment patterns (case-insensitive):
- `#` → Python, Shell, Ruby, YAML
- `//` → JavaScript, TypeScript, C, C++, Java, Go, Rust, Swift
- `/* */` → Block comments (C-style languages)
- `--` → SQL, Lua, Haskell
- `<!-- -->` → HTML, XML, Vue, Svelte
- `%` → LaTeX, Erlang

## Key Implementation Details

### Scanner behavior
- Skips binary files (images, archives, compiled files, lock files)
- Skips common build/dependency directories (node_modules, __pycache__, .git, etc.)
- Matches keywords: TODO, FIXME, HACK, XXX
- Strips trailing comment closers (`*/`, `-->`, `-}`) from matched text
- Returns absolute paths internally, displays relative paths to user

### Command execution flow
1. **Always scan first**: Before any edit/remove operation, run the scanner to get current TODO IDs
2. **Re-scan after changes**: After edit/remove, run scanner again to show updated list
3. **Context for `run`**: Use `--context 5` when executing TODOs so Claude has surrounding code
4. **Sequential edits for `run`**: Re-read files between TODO implementations to account for line number shifts

### File modification rules
- Use Edit tool, not sed/awk/manual rewrites
- Preserve comment style when editing
- Remove entire line if it contains only the TODO comment; remove only the comment if it's inline

## Installation

### Global install (recommended — works in every project)

```bash
git clone <repo-url> ~/.claude-plugins/tododo
cd ~/.claude-plugins/tododo && ./install.sh
```

This symlinks the command and skill into `~/.claude/` so `/tododo` and the
skill are available in all Claude Code sessions.

**Update:** `cd ~/.claude-plugins/tododo && ./update.sh`
**Uninstall:** `cd ~/.claude-plugins/tododo && ./uninstall.sh`

### Per-project install (git submodule)

Use when you want the plugin versioned alongside a specific project:

```bash
git submodule add <repo-url> .claude-plugins/tododo
cd .claude-plugins/tododo && ./install.sh   # installs globally from submodule path
```

Or manually link into the project only:

```bash
mkdir -p .claude/commands
ln -s ../../.claude-plugins/tododo/commands/tododo.md .claude/commands/tododo.md
ln -s ../../.claude-plugins/tododo/skills/tododo .claude/skills/tododo
```

Update a submodule: `git submodule update --remote .claude-plugins/tododo`

### What gets installed

| Path | Purpose |
|------|---------|
| `~/.claude/commands/tododo.md` | `/tododo` slash command |
| `~/.claude/skills/tododo/` | Auto-triggered skill |
