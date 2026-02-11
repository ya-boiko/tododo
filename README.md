# /tododo — TODO Manager for Claude Code

Slash command for Claude Code that manages TODO/FIXME/HACK/XXX comments in your codebase.

## Features

- **`/tododo`** or **`/tododo list`** — scan and display all TODO comments
- **`/tododo edit <id> <new text>`** — edit an existing TODO by ID
- **`/tododo remove <id>`** — remove a TODO by ID
- **`/tododo run [id...]`** — execute (implement) TODO items and remove the comment after completion

Supports comment styles: `#`, `//`, `/* */`, `--`, `<!-- -->` and more.

## Installation

### As a git submodule

```bash
# From your project root:
git submodule add git@github.com:ya-boiko/tododo.git .claude-plugins/tododo

# Link the command:
mkdir -p .claude/commands
ln -s ../../.claude-plugins/tododo/commands/tododo.md .claude/commands/tododo.md
```

### For cloning projects with this submodule

```bash
git submodule update --init
mkdir -p .claude/commands
ln -s ../../.claude-plugins/tododo/commands/tododo.md .claude/commands/tododo.md
```

### Manual (user-global)

```bash
# Available in all projects:
ln -s /path/to/tododo/commands/tododo.md ~/.claude/commands/tododo.md
```

## Updating

To update the plugin to the latest version:

```bash
# Update the submodule to the latest commit
cd .claude-plugins/tododo
git pull origin master
cd ../..

# Or update all submodules at once from project root
git submodule update --remote .claude-plugins/tododo
```

## Uninstalling

To remove the plugin from your project:

```bash
# Remove the command symlink
rm .claude/commands/tododo.md

# Remove the submodule
git submodule deinit -f .claude-plugins/tododo
git rm -f .claude-plugins/tododo
rm -rf .git/modules/.claude-plugins/tododo
```

## Requirements

- Python 3.10+
- Git (for `.gitignore`-aware scanning)

## How it works

The scanner (`scripts/scan_todos.py`) recursively walks project files respecting `.gitignore`, finds TODO/FIXME/HACK/XXX in common comment formats, and outputs a numbered list. Claude uses this list to perform edit/remove operations via the Edit tool.
