# IntelliSort - Intelligent File Organizer

A Python desktop application that automatically organizes files in any folder
(like Downloads) - not just by file type, but by recognizing related files
through filename similarity (e.g. grouping "Lecture 1", "Lecture 2" together).

## Features

- **Type-based sorting** - Images, Documents, Videos, Audio, Archives, Installers, Code
- **Smart topic grouping** - Uses fuzzy filename matching (RapidFuzz) to detect
  related files (e.g. multiple lecture slides on the same subject) and groups
  them together, regardless of file type
- **Undo system** - Every organize session is logged in a SQLite database,
  so it can be fully reversed
- **Two interfaces**:
  - Command-line (`main.py`) - for quick/scriptable use
  - Graphical (`run_gui.py`, built with PySide6) - point-and-click with
    Preview/Organize/Undo buttons
- **Standalone .exe** - packaged with PyInstaller, runs on any Windows PC
  without needing Python installed

## Project Structure

    IntelliSort/
    ├── config.py              # Category rules (extension -> folder name)
    ├── main.py                # CLI entry point
    ├── run_gui.py             # GUI entry point
    ├── core/
    │   ├── scanner.py         # Finds files in a folder
    │   ├── categorizer.py     # Decides file type category
    │   ├── grouper.py         # Groups files by filename similarity
    │   └── mover.py           # Safely moves files, avoids overwrites
    ├── database/
    │   └── history.py         # SQLite-based move logging + undo
    └── gui/
        └── main_window.py     # PySide6 window and button logic

## How It Works (High Level)

1. **Scan** - look at every file directly inside the target folder
2. **Group** - compare filenames using fuzzy matching; files that are
   similar enough (after stripping numbers/dates) get grouped into a
   shared "topic" folder
3. **Categorize** - any file that didn't match a group falls back to
   type-based sorting (Images/Documents/etc.)
4. **Move** - files are moved into their destination folder, with
   automatic renaming if a name collision would occur
5. **Log** - every move is recorded in a local SQLite database so it
   can be undone later

## Running It

**Command line:**

    python main.py <folder>              # organize a folder
    python main.py <folder> --dry-run    # preview only, nothing moves
    python main.py <folder> --undo       # reverse the last session
    python main.py                       # defaults to your Downloads folder

**GUI:**

    python run_gui.py

**Standalone .exe** (no Python required):

    dist/IntelliSort.exe

## Technologies Used

- Python 3.13
- RapidFuzz (fuzzy string matching for topic grouping)
- SQLite (via built-in `sqlite3`) for undo history
- PySide6 (Qt for Python) for the GUI
- PyInstaller for packaging into a standalone executable

## Known Limitations

- Topic grouping is based on filename similarity only (not file content) -
  in rare cases, unrelated files sharing similar numeric patterns (e.g.
  timestamps) can be grouped together
- Undo only reverses moves made *within* the target folder - it does not
  track where a file originally came from before being placed there