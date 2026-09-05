"""
config.py
---------
Central place for all settings and rules.
Keeping this separate means you can change categories WITHOUT touching
any logic code — this is called "separation of config from logic."
"""

# Maps a category folder name -> list of file extensions that belong to it
CATEGORY_MAP = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx", ".xls", ".xlsx", ".csv"],
    "Videos": [".mp4", ".mkv", ".mov", ".avi", ".wmv"],
    "Audio": [".mp3", ".wav", ".flac", ".aac"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Installers": [".exe", ".msi"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".ipynb"],
}

# Files/folders the scanner should always ignore
IGNORE_FILES = {"organizer_log.txt", "desktop.ini", ".DS_Store", "intellisort_history.db"}