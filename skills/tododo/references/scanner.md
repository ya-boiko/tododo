# scan_todos.py — Reference

## CLI Usage

```bash
python3 scan_todos.py [--context N] [root]
```

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `root` | `.` | Project root directory to scan |
| `--context N` | `2` | Lines of surrounding code to show per TODO |

### Examples

```bash
# Scan current directory with default context (2 lines)
python3 scan_todos.py .

# Show 5 lines of context (recommended for `run` operations)
python3 scan_todos.py --context 5 .

# Scan a specific project
python3 scan_todos.py /home/user/myproject
```

## Output Format

Each TODO is printed as:

```
[N] relative/path/to/file.py:LINE_NUMBER — KEYWORD: text
    |  LINE-2: surrounding code
    |  LINE-1: surrounding code
    |> LINE:   the TODO line itself
    |  LINE+1: surrounding code
    |  LINE+2: surrounding code
```

- `[N]` — 1-based index, reset on every scan run
- `relative/path/to/file.py` — path relative to the scanned root
- `LINE_NUMBER` — 1-based line number in the file
- `KEYWORD` — `TODO`, `FIXME`, `HACK`, or `XXX` (always uppercase in output)
- `text` — the comment text after the keyword and optional colon
- Context lines: `|>` marks the TODO line; `| ` marks surrounding lines

Without context (or `--context 0`), context lines are omitted:

```
[1] src/main.py:42 — TODO: Refactor this function
[2] src/utils.js:15 — FIXME: Handle null edge case
```

## Keyword Detection

Matches these keywords (case-insensitive):

| Keyword | Typical usage |
|---------|---------------|
| `TODO` | General task or planned improvement |
| `FIXME` | Known bug or broken code that needs fixing |
| `HACK` | Workaround or non-ideal solution |
| `XXX` | Attention-required, often dangerous or fragile code |

## Supported Comment Styles

| Prefix | Languages |
|--------|-----------|
| `#` | Python, Shell, Ruby, YAML, TOML |
| `//` | JavaScript, TypeScript, C, C++, Java, Go, Rust, Swift, Kotlin |
| `/* */` | C-style block comment opening (`/*`) and continuation lines (`*`) |
| `--` | SQL, Lua, Haskell |
| `<!-- -->` | HTML, XML, Vue, Svelte |
| `{- -}` | Haskell block comments |
| `%` | LaTeX, Erlang |

When editing a TODO, preserve the original comment prefix exactly as found in the file.

## File Filtering

### Git Integration

In a git repository, the scanner calls:

```bash
git ls-files --cached --others --exclude-standard
```

This includes:
- **Cached** (staged) files
- **Untracked** files not excluded by `.gitignore`

Falls back to `os.walk` with the hardcoded skip list below when `git` is unavailable or the directory is not a git repository.

### Skipped Directories

Always skipped regardless of git tracking:

```
.git            .claude         .claude-plugins
node_modules    __pycache__     .venv
venv            .tox            .mypy_cache
.pytest_cache   dist            build
.next           .nuxt           vendor
.bundle         target
```

### Skipped Files

Always skipped by filename:

```
CLAUDE.md    README.md
```

### Skipped Extensions (Binary Files)

```
Images:    .png .jpg .jpeg .gif .bmp .ico .svg .webp
Audio:     .mp3 .wav .flac .ogg
Video:     .mp4 .avi .mov .mkv
Archives:  .zip .tar .gz .bz2 .xz .7z .rar
Documents: .pdf .doc .docx .xls .xlsx .ppt .pptx
Compiled:  .exe .dll .so .dylib .o .a .class .jar .pyc .pyo .wasm
Fonts:     .woff .woff2 .ttf .eot .otf
Database:  .sqlite .db .sqlite3
Other:     .bin .lock
```

## Text Cleanup

The scanner strips trailing comment closers from matched text:

| Stripped suffix | Comment style |
|-----------------|---------------|
| `*/` | C-style block comment closer |
| `-->` | HTML comment closer |
| `-}` | Haskell block comment closer |

So `/* TODO: refactor this */` outputs `— TODO: refactor this` (without the `*/`).

## File Encoding

Files are read with `encoding="utf-8", errors="replace"` — non-UTF-8 bytes are substituted rather than raising an error. Files that cannot be opened (permissions, missing, etc.) are silently skipped.
