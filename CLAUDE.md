# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

```bash
python main.py
```

The project uses a Python 3.12 virtual environment at `.venv/`. No external dependencies — stdlib only.

## Architecture

**make-ks-api** is a CLI utility that merges source code files from a directory into organized markdown documents, primarily for preparing codebases for LLM analysis.

### Entry Point & Module Roles

- `main.py` — calls `menu()` and starts the interactive CLI
- `src/menu.py` — 4-mode interactive menu driving all operations
- `src/merge.py` — core logic: directory walking, file filtering, markdown generation
- `src/config.py` — JSON-based config persistence to `~/.merge_files_configs/`
- `src/utils.py` — path normalization, prefix stripping, filtering helpers
- `src/constants.py` — language extension maps, preset groups, excluded files/dirs

### Operation Modes (menu.py)

1. **Manual** — configure source, choose between: single output file, one file per subfolder, or file list input
2. **Saved config** — load and run a previously saved configuration
3. **List configs** — browse and execute saved configurations
4. **Path prefix** — configure a prefix to strip from absolute paths in output

### Processing Pipeline

```
Input dir / file list
  → filter by extension (PRESET_EXTENSIONS), depth (max_depth), ignore dirs, EXCLUDED_FILES
  → read with UTF-8 fallback to Latin-1
  → generate markdown: file index + syntax-highlighted code blocks
  → write to _kslist/<name>.md
```

### Key Constants (src/constants.py)

- `LANGUAGE_MAP` — maps file extensions to markdown code fence language identifiers
- `PRESET_EXTENSIONS` — 9 named groups of file extensions for common language stacks
- `EXCLUDED_FILES` — hardcoded sensitive files never included (`.env`, `secrets.json`, etc.)
- `DEFAULT_IGNORE_DIRS` — `.venv`, `.git`, `.idea`, `__pycache__`, `assets`, `_kslist`
- `CONFIG_DIR` — `~/.merge_files_configs/`

### Output

Generated markdown files are written to `_kslist/` (git-ignored) inside the scanned directory.
