"""
core/grouper.py
----------------
Job: Given a list of files, figure out which ones are "related" based
on their filenames (not extension), and group them together under a
shared topic name.

Example: "Mass Spectroscopy Lecture 1.pdf" and
"Mass Spectroscopy Lecture 2.pdf" should both be recognized as
belonging to the topic "Mass Spectroscopy Lecture".
"""

import re
from pathlib import Path
from rapidfuzz import fuzz

# How similar two normalized names need to be (0-100) to count as
# the same topic. 85 is a good starting point - strict enough to avoid
# wrongly grouping unrelated files, loose enough to catch minor differences.
SIMILARITY_THRESHOLD = 85


def normalize_name(filename: str) -> str:
    """
    Strips out the "noise" from a filename so we can compare the
    core topic. Removes: extension, trailing numbers, dates, and
    extra punctuation/whitespace.
    """
    name = Path(filename).stem

    name = re.sub(r"[\s_\-]*\d+$", "", name)
    name = re.sub(r"\d{1,4}[-_/]\d{1,2}[-_/]\d{1,4}", "", name)
    name = re.sub(r"[_\-]+", " ", name)
    name = re.sub(r"\s+", " ", name).strip()

    return name.lower()


def group_files_by_topic(files: list[Path]) -> dict[str, list[Path]]:
    """
    Groups files into topics based on filename similarity.
    """
    groups: dict[str, list[Path]] = {}
    group_display_names: dict[str, str] = {}
    no_topic_files: list[Path] = []

    for file_path in files:
        norm_name = normalize_name(file_path.name)

        if norm_name == "":
            no_topic_files.append(file_path)
            continue

        best_match = None
        best_score = 0

        for existing_key in groups.keys():
            score = fuzz.ratio(norm_name, existing_key)
            if score > best_score:
                best_score = score
                best_match = existing_key

        if best_match is not None and best_score >= SIMILARITY_THRESHOLD:
            groups[best_match].append(file_path)
        else:
            groups[norm_name] = [file_path]
            group_display_names[norm_name] = norm_name.title()

    final_groups = {
        group_display_names[key]: value for key, value in groups.items()
    }

    for file_path in no_topic_files:
        final_groups[file_path.stem] = [file_path]

    return final_groups