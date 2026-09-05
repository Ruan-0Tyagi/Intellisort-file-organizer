"""
core/mover.py
-------------
Job: Given a file and a category, safely move that file into the
right category subfolder. Handles duplicate filenames so nothing
ever gets overwritten. This module does ONE thing: moving files.
"""

import shutil
import logging
from pathlib import Path


def get_unique_destination(dest_folder: Path, filename: str) -> Path:
    """
    Avoids overwriting existing files with the same name.
    'report.pdf' -> 'report (1).pdf' -> 'report (2).pdf' etc.
    """
    dest = dest_folder / filename
    if not dest.exists():
        return dest

    stem = dest.stem
    suffix = dest.suffix
    counter = 1
    while dest.exists():
        dest = dest_folder / f"{stem} ({counter}){suffix}"
        counter += 1
    return dest


def move_file(file_path: Path, target_root: Path, category: str, dry_run: bool = False) -> Path:
    """
    Moves a single file into target_root/category/.
    Creates the category folder if it doesn't exist.
    Returns the final destination path (even in dry_run mode, for previewing).
    """
    dest_folder = target_root / category
    destination = get_unique_destination(dest_folder, file_path.name)

    if dry_run:
        return destination

    dest_folder.mkdir(exist_ok=True)
    shutil.move(str(file_path), str(destination))
    logging.info(f"MOVED: '{file_path.name}' -> '{category}/{destination.name}'")

    return destination