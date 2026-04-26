from pathlib import Path


def extract_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8")

