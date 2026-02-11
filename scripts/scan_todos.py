#!/usr/bin/env python3
"""Scan project files for TODO comments, respecting .gitignore."""

# TODO: Installation as git submodule:
#   1. git submodule add <repo-url> .claude-plugins/tododo
#   2. mkdir -p .claude/commands
#   3. ln -s ../../.claude-plugins/tododo/commands/tododo.md .claude/commands/tododo.md
#   After that /tododo command will be available in Claude Code.
#   For cloning: git submodule update --init

import argparse
import os
import re
import subprocess
import sys

# Directories and files to always skip
SKIP_DIRS = {
    ".git",
    ".claude",
    ".claude-plugins",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    "dist",
    "build",
    ".next",
    ".nuxt",
    "vendor",
    ".bundle",
    "target",
}

# Specific files to skip (documentation, etc.)
SKIP_FILES = {
    "CLAUDE.md",
    "README.md",
}

# Binary-looking extensions to skip
BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg", ".webp",
    ".mp3", ".mp4", ".avi", ".mov", ".mkv", ".flac", ".wav", ".ogg",
    ".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".exe", ".dll", ".so", ".dylib", ".o", ".a", ".class", ".jar",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".pyc", ".pyo", ".wasm", ".bin",
    ".sqlite", ".db", ".sqlite3",
    ".lock",
}

# Pattern: matches TODO in common comment styles (case-insensitive)
# Captures the TODO text after the keyword
TODO_PATTERN = re.compile(
    r"""
    (?:                     # comment prefix (non-capturing)
        \#                  # Python, Shell, Ruby, YAML
      | //                  # C, C++, Java, JS, TS, Go, Rust
      | /\*+\s*             # C-style block comment opening
      | \*\s*               # continuation line in block comment
      | --                  # SQL, Lua, Haskell
      | <!--\s*             # HTML comment opening
      | \{-\s*              # Haskell block comment
      | %                   # LaTeX, Erlang
    )
    \s*
    (TODO|FIXME|HACK|XXX)   # keyword (group 1)
    \s*[:：]?\s*             # optional colon
    (.*)                    # text (group 2)
    """,
    re.IGNORECASE | re.VERBOSE,
)


def get_git_tracked_files(root: str) -> set[str] | None:
    """Use git ls-files to get files respecting .gitignore. Returns None if not a git repo."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return None
        return {os.path.join(root, f) for f in result.stdout.splitlines() if f}
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def should_skip_file(filepath: str) -> bool:
    """Check if a file should be skipped based on extension."""
    _, ext = os.path.splitext(filepath)
    return ext.lower() in BINARY_EXTENSIONS


def should_skip_path(filepath: str) -> bool:
    """Check if a file path contains any skip directories or filenames."""
    path_parts = filepath.split(os.sep)
    # Check if any directory in the path should be skipped
    if any(part in SKIP_DIRS for part in path_parts):
        return True
    # Check if the filename itself should be skipped
    filename = os.path.basename(filepath)
    return filename in SKIP_FILES


def walk_files(root: str):
    """Yield file paths, skipping ignored directories and binary files."""
    git_files = get_git_tracked_files(root)

    if git_files is not None:
        # Git repo: use tracked + untracked (non-ignored) files
        for filepath in sorted(git_files):
            if not should_skip_file(filepath) and not should_skip_path(filepath) and os.path.isfile(filepath):
                yield filepath
    else:
        # Not a git repo: walk manually, skipping known dirs
        for dirpath, dirnames, filenames in os.walk(root):
            # Prune ignored directories (modifying dirnames in-place)
            dirnames[:] = [
                d for d in dirnames
                if d not in SKIP_DIRS and not d.startswith(".")
            ]
            dirnames.sort()

            for filename in sorted(filenames):
                filepath = os.path.join(dirpath, filename)
                if not should_skip_file(filepath):
                    yield filepath


def scan_file(filepath: str, root: str, context: int = 0) -> list[dict]:
    """Scan a single file for TODO comments.

    Returns list of dicts with keys: relpath, line_no, keyword, text,
    and optionally context_lines (list of (line_no, line_text) pairs).
    """
    results = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        for line_no_0, line in enumerate(lines):
            match = TODO_PATTERN.search(line)
            if match:
                keyword = match.group(1).upper()
                text = match.group(2).strip()
                text = re.sub(r"\s*(\*/|-->|-\})\s*$", "", text)
                relpath = os.path.relpath(filepath, root)
                entry = {
                    "relpath": relpath,
                    "line_no": line_no_0 + 1,
                    "keyword": keyword,
                    "text": text,
                }
                if context > 0:
                    start = max(0, line_no_0 - context)
                    end = min(len(lines), line_no_0 + context + 1)
                    ctx = []
                    for i in range(start, end):
                        ctx.append((i + 1, lines[i].rstrip("\n")))
                    entry["context_lines"] = ctx
                results.append(entry)
    except (OSError, UnicodeDecodeError):
        pass
    return results


def main():
    parser = argparse.ArgumentParser(description="Scan project files for TODO comments.")
    parser.add_argument("root", nargs="?", default=".", help="Project root directory")
    parser.add_argument("--context", type=int, default=0, metavar="N",
                        help="Show N lines of context around each TODO")
    args = parser.parse_args()

    root = os.path.abspath(args.root)

    if not os.path.isdir(root):
        print(f"Error: '{root}' is not a directory", file=sys.stderr)
        sys.exit(1)

    todos = []
    for filepath in walk_files(root):
        todos.extend(scan_file(filepath, root, context=args.context))

    if not todos:
        print("No TODO comments found.")
        return

    for idx, todo in enumerate(todos, start=1):
        keyword = todo["keyword"]
        label = keyword if keyword != "TODO" else "TODO"
        if todo["text"]:
            print(f"[{idx}] {todo['relpath']}:{todo['line_no']} — {label}: {todo['text']}")
        else:
            print(f"[{idx}] {todo['relpath']}:{todo['line_no']} — {label}")

        if "context_lines" in todo:
            for ctx_line_no, ctx_text in todo["context_lines"]:
                marker = ">" if ctx_line_no == todo["line_no"] else " "
                print(f"    |{marker} {ctx_line_no}: {ctx_text}")
            print()


if __name__ == "__main__":
    main()
