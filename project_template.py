from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s:')

list_of_files = [
    "docs",
    "src/__init__.py",
    "src/utils.py",
    "app.py",
    "secrets.yaml",
    ".gitignore",
    "requirements.txt",
    "working.ipynb",
]

for filepath in list_of_files:
    filepath = Path(filepath)
    if not filepath.suffix:  # If the path does not have a file extension, it's a directory
        if not filepath.exists():
            filepath.absolute().mkdir(parents=True, exist_ok=True)
            logging.info(f"Creating directory: {filepath}")
        else:
            logging.info(f"Directory {filepath} already exists")

    elif filepath.suffix:  # If the path has a file extension, it's a file
        if not filepath.exists():
            # Make sure the parent directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.touch()
            logging.info(f"Creating file: {filepath}")
        else:
            logging.info(f"File {filepath} already exists")
    else:
        logging.error(f"Unknown file type: {filepath}")
