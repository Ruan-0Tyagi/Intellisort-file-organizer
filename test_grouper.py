from pathlib import Path
from core.grouper import group_files_by_topic

test_files = [
    Path("Mass Spectroscopy Lecture 1.pdf"),
    Path("Mass Spectroscopy Lecture 2.pdf"),
    Path("Mass Spectroscopy Lecture 3.pptx"),
    Path("Mass Spectroscopy Notes.docx"),
    Path("Organic Chemistry Assignment.pdf"),
    Path("random_report.pdf"),
]

groups = group_files_by_topic(test_files)
for topic, files in groups.items():
    print(f"\n{topic}")
    for f in files:
        print(f"   - {f.name}")