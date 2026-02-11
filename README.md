# /tododo — TODO Manager for Claude Code

Slash command for Claude Code that manages TODO/FIXME/HACK/XXX comments in your codebase.

## Features

- **`/tododo`** or **`/tododo list`** — scan and display all TODO comments
- **`/tododo add <file>:<line> <text>`** — add a TODO comment with correct syntax for the file type
- **`/tododo edit <id> <new text>`** — edit an existing TODO by ID
- **`/tododo remove <id>`** — remove a TODO by ID
- **`/tododo run [id...]`** — execute (implement) TODO items and remove the comment after completion

Supports comment styles: `#`, `//`, `/* */`, `--`, `<!-- -->` and more.

## Installation

### As a git submodule

```bash
# From your project root:
git submodule add git@github-personal.com:ya-boiko/cc_todos.git .claude-plugins/todos

# Link the command:
mkdir -p .claude/commands
ln -s ../../.claude-plugins/todos/commands/tododo.md .claude/commands/tododo.md
```

### For cloning projects with this submodule

```bash
git submodule update --init
mkdir -p .claude/commands
ln -s ../../.claude-plugins/todos/commands/tododo.md .claude/commands/tododo.md
```

### Manual (user-global)

```bash
# Available in all projects:
ln -s /path/to/cc_todos/commands/tododo.md ~/.claude/commands/tododo.md
```

## Requirements

- Python 3.10+
- Git (for `.gitignore`-aware scanning)

## How it works

The scanner (`scripts/scan_todos.py`) recursively walks project files respecting `.gitignore`, finds TODO/FIXME/HACK/XXX in common comment formats, and outputs a numbered list. Claude uses this list to perform add/edit/remove operations via the Edit tool.
