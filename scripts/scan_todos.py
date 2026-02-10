#!/usr/bin/env python3
"""Scan project files for TODO comments, respecting .gitignore."""

import os
import re
import subprocess
import sys

# Directories and files to always skip
SKIP_DIRS = {
    ".git",
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


def walk_files(root: str):
    """Yield file paths, skipping ignored directories and binary files."""
    git_files = get_git_tracked_files(root)

    if git_files is not None:
        # Git repo: use tracked + untracked (non-ignored) files
        for filepath in sorted(git_files):
            if not should_skip_file(filepath) and os.path.isfile(filepath):
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


def scan_file(filepath: str, root: str) -> list[tuple[str, int, str, str]]:
    """Scan a single file for TODO comments. Returns list of (relpath, line_no, keyword, text)."""
    results = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for line_no, line in enumerate(f, start=1):
                match = TODO_PATTERN.search(line)
                if match:
                    keyword = match.group(1).upper()
                    text = match.group(2).strip()
                    # Strip trailing comment closers
                    text = re.sub(r"\s*(\*/|-->|-\})\s*$", "", text)
                    relpath = os.path.relpath(filepath, root)
                    results.append((relpath, line_no, keyword, text))
    except (OSError, UnicodeDecodeError):
        pass
    return results


def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")

    if not os.path.isdir(root):
        print(f"Error: '{root}' is not a directory", file=sys.stderr)
        sys.exit(1)

    todos = []
    for filepath in walk_files(root):
        todos.extend(scan_file(filepath, root))

    if not todos:
        print("No TODO comments found.")
        return

    # Print with sequential IDs
    for idx, (relpath, line_no, keyword, text) in enumerate(todos, start=1):
        label = keyword if keyword != "TODO" else "TODO"
        if text:
            print(f"[{idx}] {relpath}:{line_no} — {label}: {text}")
        else:
            print(f"[{idx}] {relpath}:{line_no} — {label}")


if __name__ == "__main__":
    main()
