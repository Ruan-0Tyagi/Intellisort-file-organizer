import argparse
import logging
from pathlib import Path

from core.scanner import scan_folder
from core.categorizer import get_category
from core.mover import move_file
from core.grouper import group_files_by_topic
from database.history import (
    init_db,
    new_session_id,
    log_move,
    get_last_session_id,
    undo_session,
)


def setup_logging(target_folder: Path):
    log_path = target_folder / "organizer_log.txt"
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s | %(message)s",
    )


def organize(folder_path: str, dry_run: bool = False):
    target = Path(folder_path).expanduser().resolve()

    files = scan_folder(target)
    print(f"Found {len(files)} file(s) in '{target}'\n")

    if not dry_run:
        setup_logging(target)
        init_db(target)

    session_id = new_session_id()
    topic_groups = group_files_by_topic(files)

    moved_count = 0

    for topic, grouped_files in topic_groups.items():
        if len(grouped_files) >= 2:
            for file_path in grouped_files:
                original = file_path
                destination = move_file(file_path, target, topic, dry_run=dry_run)
                label = "[DRY RUN]" if dry_run else "Moved:"
                print(f"{label} {file_path.name} -> {topic}/{destination.name}")
                if not dry_run:
                    log_move(target, session_id, original, destination)
                    moved_count += 1
        else:
            file_path = grouped_files[0]
            original = file_path
            category = get_category(file_path)
            destination = move_file(file_path, target, category, dry_run=dry_run)
            label = "[DRY RUN]" if dry_run else "Moved:"
            print(f"{label} {file_path.name} -> {category}/{destination.name}")
            if not dry_run:
                log_move(target, session_id, original, destination)
                moved_count += 1

    if dry_run:
        print("\nDry run complete. No files were actually moved.")
    else:
        print(f"\nDone! Organized {moved_count} file(s).")
        print(f"Log saved to: {target / 'organizer_log.txt'}")
        print(f"Session ID: {session_id} (use --undo to reverse this)")


def undo(folder_path: str):
    target = Path(folder_path).expanduser().resolve()

    session_id = get_last_session_id(target)
    if session_id is None:
        print("No history found - nothing to undo.")
        return

    restored = undo_session(target, session_id)
    print(f"Undo complete. Restored {restored} file(s) to their original location.")


if __name__ == "__main__"
:
    parser = argparse.ArgumentParser(description="IntelliSort - organize a folder by file type.")
    parser.add_argument(
        "folder",
        nargs="?",
        default=str(Path.home() / "Downloads"),
        help="Folder to organize (default: your Downloads folder)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would happen without moving any files",
    )
    parser.add_argument(
        "--undo",
        action="store_true",
        help="Undo the most recent organize session in this folder",
    )

    args = parser.parse_args()

    try:
        if args.undo:
            undo(args.folder)
        else:
            organize(args.folder, dry_run=args.dry_run)
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except NotADirectoryError as e:
        print(f"Error: {e}")
    except PermissionError as e:
        print(f"Error: Permission denied - is a file open in another program?\n{e}")