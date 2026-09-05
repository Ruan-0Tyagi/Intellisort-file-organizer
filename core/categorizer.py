"""
core/categorizer.py
--------------------
Job: Given a single file, decide which category it belongs to
(Images, Documents, Videos, etc.) based on its extension.
This module does ONE thing: categorizing. It doesn't scan folders,
doesn't move files.
"""

from pathlib import Path
from config import CATEGORY_MAP

# Build a reverse lookup once: extension -> category
# (Faster than looping through CATEGORY_MAP every single time)
_EXT_TO_CATEGORY = {
    ext: category
    for category, extensions in CATEGORY_MAP.items()
    for ext in extensions
}


def get_category(file_path: Path) -> str:
    """
    Returns the category name for a given file.
    Returns "Others" if the extension isn't recognized.
    """
    ext = file_path.suffix.lower()
    return _EXT_TO_CATEGORY.get(ext, "Others")