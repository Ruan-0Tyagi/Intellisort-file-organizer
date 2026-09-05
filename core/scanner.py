"""
core/scanner.py
----------------
Job: Look inside a folder and return a list of files found.
This module does ONE thing only: scanning. It doesn't move files,
doesn't categorize them — just finds them. This is the "Single
Responsibility Principle" your project spec asks for.
"""

from pathlib import Path
from config import IGNORE_FILES


def scan_folder(folder_path: str) -> list[Path]:
    """
    Looks inside folder_path (NOT subfolders) and returns a list
    of file paths found, skipping folders and ignored files.
    """
    target = Path(folder_path).expanduser().resolve()

    if not target.exists():
        raise FileNotFoundError(f"Folder does not exist: {target}")
    if not target.is_dir():
        raise NotADirectoryError(f"Not a folder: {target}")

    found_files = []

    for item in target.iterdir():
        if item.is_dir():
            continue  # skip subfolders for now
        if item.name in IGNORE_FILES:
            continue
        found_files.append(item)

    return found_files